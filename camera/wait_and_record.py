import cv2
import datetime
import firebase_admin
import json
import os
import threading
import logging

from firebase_admin import firestore
from google.cloud import pubsub_v1
from google.cloud import storage

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Project and topic/subscription information
GC_PROJECT_ID = os.environ["GC_PROJECT_ID"]
PUBSUB_SUBSCRIPTION_ID = os.environ["PUBSUB_SUBSCRIPTION_ID"]
GCS_BUCKET_NAME = os.environ["GCS_BUCKET_NAME"]
FS_DATABASE_ID = os.environ['FS_DATABASE_ID']
FS_COLLECTION_NAME = os.environ["FS_COLLECTION_NAME"]
STATION_ID = os.environ['STATION_ID']

# Initialize Pub/Sub subscriber client
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(GC_PROJECT_ID, PUBSUB_SUBSCRIPTION_ID)

# Initialize Firestore client
if not firebase_admin._apps:
    default_app = firebase_admin.initialize_app()
    db = firestore.client(database_id=FS_DATABASE_ID)
    
# Initialize Cloud Storage client
storage_client = storage.Client()
bucket = storage_client.bucket(GCS_BUCKET_NAME)

# Global variables to control streaming
streaming_active = False
video_writer = None
stop_video_thread = threading.Event()


def process_message(message: pubsub_v1.subscriber.message.Message):
    """Processes Pub/Sub messages."""
    global streaming_active, video_writer, stop_video_thread
    try:
        data = json.loads(message.data.decode("utf-8"))
        logger.info(f"Received message: {data}")

        game_id = data["gameId"]
        filename = "track-view.mp4"
        if data["command"] == "start-recording":
            if not streaming_active:
                logger.info("Starting recording...")
                streaming_active = True
                stop_video_thread.clear()  # Ensure the thread is not stopped
                start_video_thread()

                update_station_status(game_id=game_id)
                update_game_status(game_id=game_id, status="Playing")
            else:
                logger.warn("Already recording. New command ignored...")

        else:
            if streaming_active:
                streaming_active = False
                stop_video_thread.set()  # Signal the thread to stop

                if video_writer:
                    video_writer.release()
                    video_writer = None

            if data["command"] == "cancel-recording":
                logger.info("Cancelling recording...")
                update_station_status(game_id="NA")
                update_game_status(game_id=game_id, status="Cancelled")

            elif data["command"] == "stop-recording":
                logger.info("Stopping recording...")
                update_station_status(game_id="NA")
                update_game_status(game_id=game_id, status="Completed")

        message.ack()

    except Exception as e:
        logger.info(f"Error processing message: {e}")
        message.nack()  # Don't acknowledge the message if there is an issue.


def start_video_thread():
    """Starts the video capture and upload thread."""
    video_thread = threading.Thread(target=capture_video)
    video_thread.daemon = True  # allow the main thread to exit even if this thread is running
    video_thread.start()


def capture_video():
    """Captures webcam footage and uploads it to Cloud Storage."""
    global video_writer

    cap = cv2.VideoCapture(0)  # Open the default webcam (0)
    if not cap.isOpened():
        logger.error("Error: Could not open webcam.")
        return

    try:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use MP4 codec
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"webcam_{timestamp}.mp4"
        video_writer = cv2.VideoWriter(filename, fourcc, 30.0, (int(cap.get(3)), int(cap.get(4))))  # 30 FPS

        while streaming_active and not stop_video_thread.is_set():
            ret, frame = cap.read()
            if not ret:
                logger.error("Error: Could not read frame.")
                break

            video_writer.write(frame)

        if video_writer:
            video_writer.release()

        cap.release()

    except Exception as e:
        logger.error(f"Video capture/upload error: {e}")

    finally:
        cap.release()


def upload_video_to_gcs(game_id, filename):
    if os.path.exists(filename):
        blob = bucket.blob(filename)
        blob.upload_from_filename(filename)
        logger.info(f"Video uploaded to gs://{GCS_BUCKET_NAME}/{game_id}/{filename}")
        os.remove(filename)  # Clean up local file


def callback(message: pubsub_v1.subscriber.message.Message):
    """Callback function for Pub/Sub messages."""
    process_message(message)


def update_station_status(game_id: str):
    """
    This function does 2 things in `game-stations` Firestore document:
    - toggle isRunning field
    - update gameId field
    """
    if db:
        try:
            doc_ref = db.collection("game-stations").document(f"station{STATION_ID}")
            doc = doc_ref.get()

            if doc.exists:
                is_running = doc.to_dict()['isRunning']
                new_is_running = not is_running
                doc_ref.update({
                    "isRunning": new_is_running,
                })
                doc_ref.update({"gameId": game_id})
                logger.info(f"game-stations doc updated with gameId: '{game_id}' and "
                            f"isRunning: '{new_is_running}' for Station {STATION_ID}")
            else:
                logger.error(f"game-stations doc not found for Station {STATION_ID}")
        except Exception as e:
            logger.error(f"Error updating game-stations doc")
            raise e
    else:
        raise Exception("Firestore not initialized")


def update_game_status(game_id, status):
    """
    Updates a specific field in a Firestore document.
    """
    if db:
        try:
            doc_ref = db.collection("game-sessions").document(game_id)
            if status != "Playing":
                now = datetime.datetime.now(datetime.timezone.utc)  # Ensure UTC Time.
                doc_ref.update({
                    "gameStatus": status,
                    "endDateTime": now
                })
            else:
                doc_ref.update({"gameStatus": status})
            logger.info(f"Updated gameStatus: '{status}' to gameId: '{game_id}'")
        except Exception as e:
            logger.error(f"Error updating gameStatus: '{status}' to gameId: '{game_id}'")
            raise e
    else:
        raise Exception("Firestore not initialized")


def main():
    """Main function to start Pub/Sub subscriber."""
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    logger.info(f"Listening for messages on {subscription_path}...")

    try:
        streaming_pull_future.result()  # Blocks indefinitely until a signal is received.
    except KeyboardInterrupt:
        logger.error("Stopping subscriber...")
        streaming_pull_future.cancel()
        streaming_pull_future.result()  # Block until the shutdown is complete.
    finally:
        logger.info("Subscriber stopped.")


if __name__ == "__main__":
    main()
