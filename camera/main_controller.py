import time
import datetime
import logging
import os
import signal
import sys
import threading
import re
import json
from typing import Optional, Dict

# --- Google Cloud Imports ---
from google.cloud import pubsub_v1, storage
from google.cloud.exceptions import NotFound, Conflict, GoogleCloudError
from google.auth.exceptions import DefaultCredentialsError

import config as cfg
from services.pubsub_listener import PubSubListener
from services.pubsub_publisher import PubSubPublisher
from services.gcs_uploader import GCSUploader
from utils.webcam_recorder import WebcamRecorder
from utils.processing_pipelines import get_processor, ScoreEvent

log = logging.getLogger(__name__)


class MainController:
    """Orchestrates webcam recording based on Pub/Sub commands."""

    def __init__(self):
        self.recorders: Dict[int, WebcamRecorder] = {}
        self.uploader: Optional[GCSUploader] = None
        self.listener: Optional[PubSubListener] = None
        self.publisher: Optional[PubSubPublisher] = None
        self._is_rec = False
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self.game_id: Optional[str] = None
        self.score_count: int = 0
        self._initialize_components()

    def _check_gc_resources(self):
        """Checks for and creates necessary GCP resources if they don't exist."""
        log.info("----- Checking required GCP resources -----")
        project_id = cfg.GOOGLE_CLOUD_PROJECT_ID
        topic_id = cfg.PUBSUB_TOPIC_ID
        subscription_id = cfg.PUBSUB_SUBSCRIPTION_ID
        bucket_name = cfg.GCS_BUCKET_NAME
        bucket_location = getattr(cfg, 'GOOGLE_CLOUD_REGION', 'US')  # Default to US if not set

        # --- Check/Create GCS Bucket ---
        try:
            storage_client = storage.Client(project=project_id)
            try:
                storage_client.get_bucket(bucket_name)
                log.info(f"GCS Bucket '{bucket_name}' already exists. No action needed.")
            except NotFound:
                log.warning(
                    f"GCS Bucket '{bucket_name}' not found. Attempting to create in location '{bucket_location}'...")
                try:
                    storage_client.create_bucket(bucket_name, location=bucket_location)
                    log.info(f"Successfully created GCS Bucket '{bucket_name}'.")
                except Conflict:
                    log.warning(f"GCS Bucket '{bucket_name}' already exists (likely created recently).")
                except GoogleCloudError as e:
                    log.error(f"Failed to create GCS bucket '{bucket_name}': {e}. Check permissions (Storage Admin?).")
                    raise RuntimeError(f"Bucket creation failed: {e}") from e
        except DefaultCredentialsError as e:
            log.critical(f"GCS Authentication error: {e}")
            raise RuntimeError("GCS Authentication failed") from e
        except Exception as e:
            log.critical(f"Unexpected error checking/creating GCS bucket: {e}", exc_info=True)
            raise

        # --- Check/Create Pub/Sub Topic ---
        topic_path = None
        try:
            publisher_client = pubsub_v1.PublisherClient()
            topic_path = publisher_client.topic_path(project_id, topic_id)
            try:
                publisher_client.get_topic(request={"topic": topic_path})
                log.info(f"Pub/Sub Topic '{topic_id}' already exists. No action needed.")
            except NotFound:
                log.warning(f"Pub/Sub Topic '{topic_id}' not found. Attempting to create...")
                try:
                    publisher_client.create_topic(request={"name": topic_path})
                    log.info(f"Successfully created Pub/Sub Topic '{topic_id}'.")
                except Conflict:
                    log.warning(f"Pub/Sub Topic '{topic_id}' already exists (likely created recently).")
                except GoogleCloudError as e:
                    log.error(f"Failed to create Pub/Sub topic '{topic_id}': {e}. Check permissions (Pub/Sub Admin?).")
                    raise RuntimeError(f"Topic creation failed: {e}") from e
        except DefaultCredentialsError as e:
            log.critical(f"Pub/Sub Authentication error: {e}")
            raise RuntimeError("Pub/Sub Authentication failed") from e
        except Exception as e:
            log.critical(f"Unexpected error checking/creating Pub/Sub topic: {e}", exc_info=True)
            raise

        # --- Check/Create Pub/Sub Subscription ---
        if not topic_path:  # Ensure topic path was determined
            raise RuntimeError("Cannot proceed without a valid Pub/Sub topic path.")
        try:
            subscriber_client = pubsub_v1.SubscriberClient()
            subscription_path = subscriber_client.subscription_path(project_id, subscription_id)
            try:
                subscriber_client.get_subscription(request={"subscription": subscription_path})
                log.info(f"Pub/Sub Subscription '{subscription_id}' already exists. No action needed.")
            except NotFound:
                log.warning(
                    f"Pub/Sub Subscription '{subscription_id}' not found. Attempting to create for topic '{topic_id}'...")
                try:
                    # Default ack deadline is 10s, adjust if needed
                    subscriber_client.create_subscription(request={
                        "name": subscription_path,
                        "topic": topic_path,
                        # "ack_deadline_seconds": 60, # Optional: customize
                    })
                    log.info(f"Successfully created Pub/Sub Subscription '{subscription_id}'.")
                except Conflict:
                    log.warning(f"Pub/Sub Subscription '{subscription_id}' already exists (likely created recently).")
                except GoogleCloudError as e:
                    log.error(
                        f"Failed to create subscription '{subscription_id}': {e}. "
                        f"Check permissions (Pub/Sub Admin?) and ensure topic exists.")
                    raise RuntimeError(f"Subscription creation failed: {e}") from e
        except DefaultCredentialsError as e:
            log.critical(f"Pub/Sub Authentication error: {e}")
            raise RuntimeError("Pub/Sub Authentication failed") from e
        except Exception as e:
            log.critical(f"Unexpected error checking/creating Pub/Sub subscription: {e}", exc_info=True)
            raise

        log.info("----- GCP resource check/creation complete. -----")

    def _initialize_components(self):
        """Initializes components after ensuring resources exist."""
        log.info("Initializing components...")
        try:
            if cfg.CHECK_GOOGLE_CLOUD_RESOURCES:
                self._check_gc_resources()

            self.uploader = GCSUploader(cfg.GCS_BUCKET_NAME)
            if not self.uploader.is_ready():  # Should be ready now, but double-check
                raise RuntimeError("GCS Uploader failed post-check.")

            self.publisher = PubSubPublisher(cfg.GOOGLE_CLOUD_PROJECT_ID, cfg.PUBSUB_TOPIC_ID)
            if not self.publisher.is_ready():
                # This might still fail if permissions are only for create, not use
                log.warning("Pub/Sub Publisher check failed post-creation attempt.")

            # Create Recorders
            for conf in cfg.WEBCAM_CONFIGS:
                source = conf.get("source")
                output_filename = conf.get("output_filename")
                key = conf.get("processing_key")
                if source is None: continue
                proc = get_processor(key, score_callback=self._on_score)
                self.recorders[source] = WebcamRecorder(source, cfg.OUTPUT_DIR, output_filename, cfg.VIDEO_FPS,
                                                        cfg.VIDEO_RESOLUTION, processor=proc)
                log.info(f"Initialized recorder {source} with (Processor: {key or 'None'})")

            self.listener = PubSubListener(cfg.GOOGLE_CLOUD_PROJECT_ID, cfg.PUBSUB_SUBSCRIPTION_ID, self.handle_msg)
            if not self.listener.is_ready():
                raise RuntimeError("Pub/Sub Listener failed post-check.")

            log.info("All components initialized successfully.")

        except Exception as e:  # Catch errors from resource creation or component init
            log.critical(f"Fatal error during controller initialization: {e}", exc_info=True)
            raise

    def _on_score(self, score_details: ScoreEvent):
        """Callback triggered by processor on score detection."""
        with self._lock:
            if not self._is_rec or self.game_id is None: return
            self.score_count += 1
            _, score_val, hole_id = score_details
            log.info(
                f"SCORE: Game='{self.game_id}', Count={self.score_count}/{cfg.SCORES_PER_GAME_SESSION} (+{score_val})")
            if self.score_count >= cfg.SCORES_PER_GAME_SESSION:
                log.info(f"Score limit per round ({cfg.SCORES_PER_GAME_SESSION} scores) reached for '{self.game_id}'.")
                self._stop_rec(self.game_id, reason="Round End")
                # if self.publisher and self.publisher.is_ready():
                #     threading.Thread(target=self.publisher.publish_message,
                #                      args=(b'{"command": "stop-recording", "reason": "round_end"}',),
                #                      kwargs={'game_id': self.game_id}, daemon=True).start()
                # else:
                #     log.warning("Cannot publish stop: Publisher not ready.")

    def handle_msg(self, msg_data: str):
        """Handles incoming Pub/Sub commands (expects JSON)."""
        try:
            data = json.loads(msg_data)
            command = data.get("command").lower()
            game_id = data.get("gameId")
            reason = data.get("reason")

            if command == "start-recording":
                self._start_rec(game_id, reason)
            elif command == "stop-recording":
                self._stop_rec(game_id, reason)
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
                return log.warning(f"Already recording '{self.game_id}', ignoring start for '{game_id}'.")
            self._is_rec = True
            self.game_id = game_id
            self.score_count = 0
            log.info(f"STARTING Recording Session: GameID='{self.game_id}' - (Reason: {reason})")

        started = 0
        for cid, rec in self.recorders.items():  # Start sequentially
            log.info(f"Starting cam {cid}...")
            if rec.start_recording():
                started += 1
            else:
                log.error(f"Failed start cam {cid}")
        log.info(f"Started {started}/{len(self.recorders)} recorders.")
        if started == 0 and self.recorders:
            with self._lock: self._is_rec = False; self.game_id = None

    def _stop_rec(self, game_id: str, reason: str = "unknown"):
        """Stops recording session."""
        with self._lock:
            if not self._is_rec: return
            log.info(f"STOPPING Recording Session: GameID='{self.game_id}' - (Reason: {reason})")
            self._is_rec = False
            game_id_stopped = self.game_id
            self.game_id = None
            self.score_count = 0

        stopped_files = []
        summaries = {}
        for cid, rec in self.recorders.items():  # Stop sequentially
            if rec.is_recording or (rec.thread and rec.thread.is_alive()):
                original, annotated = rec.stop_recording()
                if original: stopped_files.append(original)
                if annotated: stopped_files.append(annotated)

                try:  # Get summary
                    proc = rec.get_processor()
                    summ = proc.get_summary() if proc and hasattr(proc, 'get_summary') else None
                    if summ: summaries[cid] = summ
                except Exception as e:
                    log.error(f"Summary error cam {cid}: {e}")

        log.info(f"Stopped recorders for game '{game_id_stopped}'.")

        # Upload
        if stopped_files and self.uploader and self.uploader.is_ready():
            log.info(f"Queueing {len(stopped_files)} files for upload...")
            safe_gid_path = re.sub(r'[\\/*?:"<>|]', "_", game_id_stopped or "no_id")
            for file_path in stopped_files:
                blob_name = f"recordings/game_{safe_gid_path}/{os.path.basename(file_path)}"
                # self.uploader.upload_async(file_path, blob_name, game_id, delete_local=False)

        # Print Summaries
        log.info(f"----- Summary: GameID: {game_id_stopped} -----")
        if not summaries:
            log.info("No summaries.")
        else:
            for cid, summ_data in summaries.items():
                log.info(f" Cam {cid}:")
                if isinstance(summ_data, dict) and "final_score" in summ_data:
                    log.info(f"  Score: {summ_data['final_score']}")
                    evts = summ_data.get('scored_events', [])
                    log.info(f"  Events ({len(evts)}): " + (
                        ", ".join([f"+{s}({h})" for _, s, h in evts]) if evts else "None"))
                elif summ_data:
                    log.info(f"  {summaries}")
        log.info("-------------------------------------")

    def run(self):
        """Starts listener and waits for shutdown signal."""
        if not self.listener or not self.listener.is_ready():
            return log.critical("Listener not ready.")

        log.info("Starting Pub/Sub listener...")
        self.listener.listen()
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
        if self.listener: self.listener.stop()
        if self._is_rec: self._stop_rec("shutdown")
        if self.publisher: self.publisher.close()
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
