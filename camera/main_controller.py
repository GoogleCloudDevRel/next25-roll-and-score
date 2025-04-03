import json
import logging
import os
import signal
import sys
import threading
import time
from typing import Optional, Dict

import config as cfg
from services.firestore_updater import FirestoreUpdater
from services.gcs_uploader import GCSUploader
from services.gemini_coach import GeminiCoach
from services.pubsub_listener import PubSubListener
from services.pubsub_publisher import PubSubPublisher
from utils.processing_pipelines import get_processor, ScoreEvent
from utils.resources_checker import ensure_gcp_resources
from utils.webcam_recorder import WebcamRecorder

from google.cloud import firestore

log = logging.getLogger(__name__)


class MainController:
    """Orchestrates webcam recording based on Pub/Sub commands."""

    def __init__(self):
        self.recorders: Dict[int, WebcamRecorder] = {}
        self.gcs_uploader: Optional[GCSUploader] = None
        self.pubsub_listener: Optional[PubSubListener] = None
        self.pubsub_publisher: Optional[PubSubPublisher] = None
        self.firestore_updater: Optional[FirestoreUpdater] = None
        self.gemini_coach: Optional[GeminiCoach] = None
        self._is_rec = False
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self.game_id: Optional[str] = None
        self.round_number: Optional[int] = None
        self.scores_from_all_rounds: list[int] = []
        self.score_count: int = 0
        self._initialize_components()

    def _initialize_components(self):
        """Initializes components after ensuring resources exist."""
        log.info("Initializing components...")
        try:
            if cfg.ENSURE_RESOURCES:
                ensure_gcp_resources(
                    project_id=cfg.GOOGLE_CLOUD_PROJECT_ID,
                    topic_id=cfg.PUBSUB_TOPIC_ID,
                    subscription_id=cfg.PUBSUB_SUBSCRIPTION_ID,
                    bucket_name=cfg.GCS_BUCKET_NAME,
                    bucket_location=cfg.GCS_BUCKET_LOCATION,
                    database_id=cfg.FIRESTORE_DATABASE_ID
                )

            # --- Initialize GCS Uploader ---
            self.gcs_uploader = GCSUploader(cfg.GCS_BUCKET_NAME)
            if not self.gcs_uploader.is_ready():  # Should be ready now, but double-check
                raise RuntimeError("GCS Uploader failed post-check.")

            # --- Initialize PubSub Publisher ---
            self.pubsub_publisher = PubSubPublisher(cfg.GOOGLE_CLOUD_PROJECT_ID, cfg.PUBSUB_TOPIC_ID)
            if not self.pubsub_publisher.is_ready():
                # This might still fail if permissions are only for create, not use
                log.warning("Pub/Sub Publisher check failed post-creation attempt.")

            # --- Initialize PubSub Listener ---
            self.pubsub_listener = PubSubListener(
                cfg.GOOGLE_CLOUD_PROJECT_ID,
                cfg.PUBSUB_SUBSCRIPTION_ID,
                self.handle_msg)
            if not self.pubsub_listener.is_ready():
                raise RuntimeError("Pub/Sub Listener failed post-check.")

            # --- Initialize Firestore Updater ---
            self.firestore_updater = FirestoreUpdater(
                project_id=cfg.GOOGLE_CLOUD_PROJECT_ID,
                database_id=cfg.FIRESTORE_DATABASE_ID
            )
            if not self.firestore_updater.is_ready():
                raise RuntimeError("Firestore updater failed post-check.")

            # --- Initialize Gemini Coach ---
            self.gemini_coach = GeminiCoach(
                project_id=cfg.GOOGLE_CLOUD_PROJECT_ID,
                location=cfg.GOOGLE_CLOUD_REGION,
                model_id=cfg.GEMINI_MODEL_ID,
                system_instruction=cfg.GEMINI_SYSTEM_INSTRUCTION,
                prompt_template=cfg.GEMINI_PROMPT_TEMPLATE
            )

            #  --- Create Recorders ---
            for conf in cfg.WEBCAM_CONFIGS:
                source = conf.get("source")
                output_filename = conf.get("output_filename")
                key = conf.get("processing_key")
                if source is None: continue
                proc = get_processor(key, score_callback=self._on_score)
                self.recorders[source] = WebcamRecorder(
                    webcam_id=source,
                    output_dir=cfg.OUTPUT_DIR,
                    output_filename=output_filename,
                    fps=cfg.VIDEO_FPS,
                    resolution=cfg.VIDEO_RESOLUTION,
                    codec=cfg.VIDEO_CODEC,
                    processor=proc,
                )
                log.info(f"Initialized recorder {source} with (Processor: {key or 'None'})")

            log.info("All components initialized successfully.")

        except Exception as e:  # Catch errors from resource creation or component init
            log.critical(f"Fatal error during controller initialization: {e}", exc_info=True)
            raise

    def _on_score(self, score_details: ScoreEvent):
        """Callback triggered by processor on score detection."""
        with (self._lock):
            if not self._is_rec or self.game_id is None: return
            self.score_count += 1
            _, score_val, hole_id = score_details
            log.info(
                f"SCORE: Game='{self.game_id}', Count={self.score_count}/{cfg.SCORES_PER_GAME_SESSION} (+{score_val})")
            if self.score_count <= cfg.SCORES_PER_GAME_SESSION:
                self.scores_from_all_rounds.append(score_val)

                # Update score to the firestore to display
                self._update_game_session(
                    field_updates={
                        "scores": self.scores_from_all_rounds,
                        "totalScore": sum(self.scores_from_all_rounds)
                    }
                )

            if self.score_count == cfg.SCORES_PER_GAME_SESSION:
                log.info(f"Score limit per round ({cfg.SCORES_PER_GAME_SESSION} scores) reached for '{self.game_id}'. "
                         f"Ending this round...")
                if self.pubsub_publisher and self.pubsub_publisher.is_ready():
                    message = {
                        "command": "stop-recording",
                        "gameId": self.game_id,
                        "reason": "round-end"
                    }
                    byte_message = json.dumps(message).encode('utf-8')
                    threading.Thread(target=self.pubsub_publisher.publish_message,
                                     args=(byte_message,),
                                     daemon=True).start()
                else:
                    log.warning("Cannot publish message: Publisher not ready.")

    def handle_msg(self, msg_data: str):
        """Handles incoming Pub/Sub commands (expects JSON)."""
        try:
            data = json.loads(msg_data)
            command = data.get("command").lower()
            game_id = data.get("gameId")
            reason = data.get("reason").lower().strip().replace(' ', '-')

            if command == "start-recording":
                code = self._start_rec(game_id, reason)
                if code != -1:
                    self.round_number = int(data.get("round", 1))
                    if self.round_number == 1: self.scores_from_all_rounds = []
                    self._update_station_info(field_updates={
                        "gameId": game_id,
                        "isRunning": True
                    })
                    self._update_game_session(field_updates={
                        "gameStatus": "inProgress",
                    })

            elif command == "stop-recording":
                if game_id != self.game_id:
                    log.warning(f"Current game session is not '{game_id}'. Command ignored!")
                    return
                else:
                    with self._lock:
                        if not self._is_rec: return

                recorded_files = self._stop_rec(reason)
                if reason != "cancellation":
                    gcs_video_uri_list = self._upload_files(recorded_files[:1], upload_async=False)
                    lane_view_video_uri = gcs_video_uri_list[0]

                    # Update replayVideo field
                    public_video_url = lane_view_video_uri.replace("gs://", "https://storage.googleapis.com/")
                    print(public_video_url)
                    self._update_station_info(field_updates={"replayVideo": public_video_url})

                    # Update geminiFeedback field
                    gemini_feedback = self.gemini_coach.generate_feedback(lane_view_video_uri)
                    self._update_station_info(field_updates={"geminiFeedback": gemini_feedback})

                    # Add video with feedback and game status to game-sessions collection
                    new_vid_with_feedback = {"video": public_video_url, "feedback": gemini_feedback}
                    if self.round_number < cfg.TOTAL_NUMBER_OF_ROUNDS:
                        self._update_game_session(field_updates={
                            "recordingsWithFeedback": firestore.ArrayUnion([new_vid_with_feedback]),
                        })
                    else:
                        self._update_game_session(field_updates={
                            "recordingsWithFeedback": firestore.ArrayUnion([new_vid_with_feedback]),
                            "gameStatus": "completed"
                        })

                    # Upload remaining files
                    self._upload_files(recorded_files[1:])

                    # Update isRunning field
                    self._update_station_info(field_updates={"isRunning": False})

                    log.info(f"Successfully ended round: {self.round_number} for game: '{self.game_id}'")
                else:
                    self._update_station_info(field_updates={
                        "gameId": "",
                        "replayVideo": "",
                        "geminiFeedback": "",
                        "isRunning": False,
                    })
                    self._update_game_session(field_updates={"gameStatus": "cancelled"})
            else:
                log.warning(f"Unrecognized command: '{command}' in received message: {data}.")

        except json.JSONDecodeError:
            log.error(f"Failed to parse Pub/Sub message as JSON: {msg_data[:100]}...")
        except Exception as e:
            log.error(f"Error handling message: {e}", exc_info=True)

    def _start_rec(self, game_id: str, reason: str = "unknown"):
        """Starts recording session."""

        with self._lock:
            if self._is_rec:
                log.warning(f"Already recording '{self.game_id}', ignoring start for '{game_id}'.")
                return -1
            self._is_rec = True
            self.game_id = game_id
            self.score_count = 0
            log.info(f"STARTING Recording Session: Game: '{self.game_id}', Round: {self.round_number}, Reason: {reason}")

        started = 0
        for cid, rec in self.recorders.items():  # Start sequentially
            log.info(f"Starting cam {cid}...")
            if rec.start_recording():
                started += 1
            else:
                log.error(f"Failed start cam {cid}")
        log.info(f"Started {started}/{len(self.recorders)} recorders.")
        if started == 0 and self.recorders:
            with self._lock: self._is_rec = False

    def _stop_rec(self, reason: str = "unknown"):
        """Stops recording session."""
        with self._lock:
            if not self._is_rec:
                return -1
            log.info(f"STOPPING Recording Session: GameID='{self.game_id}' - (Reason: {reason})")
            self._is_rec = False
            # game_id_stopped = self.game_id
            # self.game_id = None
            self.score_count = 0

        stopped_files = []
        summaries = {}
        for cid, rec in self.recorders.items():  # Stop sequentially
            if rec.is_recording or (rec.thread and rec.thread.is_alive()):
                original, annotated = rec.stop_recording()
                if original: stopped_files.append(original)
                if annotated: stopped_files.append(annotated)

                # try:  # Get summary
                #     proc = rec.get_processor()
                #     summ = proc.get_summary() if proc and hasattr(proc, 'get_summary') else None
                #     if summ: summaries[cid] = summ
                # except Exception as e:
                #     log.error(f"Summary error cam {cid}: {e}")
        log.info(f"Stopped recorders for game '{self.game_id}'.")
        return stopped_files

    def _upload_files(self, files_to_upload: list[str], make_public: bool = True,
                      delete_local: bool = cfg.DELETE_LOCAL_RECORDINGS, upload_async: bool = True):
        gcs_video_uri_list = []
        if self.gcs_uploader and self.gcs_uploader.is_ready():
            log.info(f"Queueing {len(files_to_upload)} files for upload...")
            for file_path in files_to_upload:
                filename, file_extension = os.path.splitext(os.path.basename(file_path))
                new_filename = f"{filename}_round{self.round_number}{file_extension}"

                blob_name = f"recordings/{self.game_id}/{new_filename}"
                self.gcs_uploader.upload_file(file_path, blob_name, make_public=make_public,
                                              delete_local=delete_local, upload_async=upload_async)

                gcs_video_uri = f"gs://{cfg.GCS_BUCKET_NAME}/{blob_name}"
                gcs_video_uri_list.append(gcs_video_uri)

            return gcs_video_uri_list
        else:
            log.error("GCS Uploader is not ready!")

    def _update_game_session(self, field_updates):
        """
        Helper function to update the document in Firestore.
        """
        if self.firestore_updater and self.firestore_updater.is_ready() and self.game_id:
            log.info(f"Attempting to update Firestore for game: '{self.game_id}'...")

            # Call the method on the FirestoreUpdater instance
            success = self.firestore_updater.update_document(
                collection_name=cfg.GAME_SESSIONS_COLLECTION_NAME,
                document_id=self.game_id,
                field_updates=field_updates
            )
            if success:
                log.info(f"Firestore update successful for game '{self.game_id}'.")
            else:
                log.error(f"Firestore update failed for game '{self.game_id}'.")

    def _update_station_info(self, field_updates: dict):
        """
        Helper function to update the document in Firestore.
        """
        collection_name = cfg.STATION_INFO_COLLECTION_NAME
        document_id = cfg.STATION_ID

        if self.firestore_updater and self.firestore_updater.is_ready() and document_id:
            log.info(f"Attempting to update Firestore Document: '{document_id}' with {field_updates}...")

            success = self.firestore_updater.update_document(
                collection_name=collection_name,
                document_id=document_id,
                field_updates=field_updates
            )
            if success:
                log.info(f"Firestore update successful for document: '{document_id}'.")
            else:
                log.error(f"Firestore update failed for document: '{document_id}'.")

    def _print_summary(self, summaries: dict):
        log.info(f"----- Summary: GameID: {self.game_id} -----")
        if not summaries:
            log.info("No summaries.")
        else:
            for cid, summ_data in summaries.items():
                log.info(f" Cam {cid}:")
                if isinstance(summ_data, dict) and "final_score" in summ_data:
                    log.info(f"  Score: {summ_data['final_score']}")
                    events = summ_data.get('scored_events', [])
                    log.info(f"  Events ({len(events)}): " + (
                        ", ".join([f"+{s}({h})" for _, s, h in events]) if events else "None"))
                elif summ_data:
                    log.info(f"  {summaries}")
        log.info("-------------------------------------")

    def run(self):
        """Starts listener and waits for shutdown signal."""
        if not self.pubsub_listener or not self.pubsub_listener.is_ready():
            return log.critical("Listener not ready.")

        log.info("Starting Pub/Sub listener...")
        self.pubsub_listener.listen()
        log.info("Controller running. Press Ctrl+C to shutdown.")

        try:
            while not self._stop.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            log.info("Ctrl+C received.")
        finally:
            self.shutdown()

    def shutdown(self):
        """Initiates shutdown."""
        if self._stop.is_set(): return

        log.info("----- Shutting Down -----")
        self._stop.set()
        if self.pubsub_listener: self.pubsub_listener.stop()
        if self._is_rec: self._stop_rec("shutdown")
        if self.pubsub_publisher: self.pubsub_publisher.close()

        self._update_station_info(field_updates={
            "gameId": "",
            "replayVideo": "",
            "geminiFeedback": "",
            "isRunning": False,
        })

        time.sleep(1)
        log.info("----- Shutdown Complete -----")


# --- Main Execution ---
if __name__ == "__main__":
    controller: Optional[MainController] = None


    def handle_signal(sig, frame):
        log.warning(f"Received signal {signal.Signals(sig).name}. Shutting down...")
        if controller and not controller._stop.is_set():
            controller.shutdown()
        else:
            sys.exit(0)  # Exit directly if controller isn't running

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    try:
        log.info(f"Application starting (PID: {os.getpid()})...")
        controller = MainController()
        controller.run()
    except Exception as e:
        log.critical(f"Application failed: {e}", exc_info=True)
    finally:
        log.info("Application finished.")
