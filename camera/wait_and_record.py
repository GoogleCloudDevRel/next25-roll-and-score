import cv2
import os
from google.cloud import pubsub_v1
from google.cloud import storage
import datetime
import threading
import json

# Project and topic/subscription information
project_id = os.environ["PROJECT_ID"]
subscription_id = os.environ["PUBSUB_SUBSCRIPTION_ID"]
bucket_name = os.environ["GCS_BUCKET_NAME"]

# Initialize Pub/Sub subscriber client
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_id)

# Initialize Cloud Storage client
storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)

# Global variables to control streaming
streaming_active = False
video_writer = None
stop_video_thread = threading.Event()


def process_message(message: pubsub_v1.subscriber.message.Message):
    """Processes Pub/Sub messages."""
    global streaming_active, video_writer, stop_video_thread
    try:
        data = json.loads(message.data.decode("utf-8"))
        print(f"Received message: {data}")

        if data["commend"] == "start-streaming":
            if not streaming_active:
                print("Starting streaming...")
                streaming_active = True
                stop_video_thread.clear()  # Ensure the thread is not stopped
                start_video_thread()

        elif data["commend"] == "stop-streaming":
            if streaming_active:
                print("Stopping streaming...")
                streaming_active = False
                stop_video_thread.set()  # Signal the thread to stop
                if video_writer:
                    video_writer.release()
                    video_writer = None

        message.ack()

    except Exception as e:
        print(f"Error processing message: {e}")
        message.nack()  # Don't acknowledge the message if there is an issue.


def start_video_thread():
    """Starts the video capture and upload thread."""
    video_thread = threading.Thread(target=capture_and_upload)
    video_thread.daemon = True  # allow the main thread to exit even if this thread is running
    video_thread.start()


def capture_and_upload():
    """Captures webcam footage and uploads it to Cloud Storage."""
    global video_writer

    cap = cv2.VideoCapture(0)  # Open the default webcam (0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    try:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use MP4 codec
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"webcam_{timestamp}.mp4"
        video_writer = cv2.VideoWriter(filename, fourcc, 30.0, (int(cap.get(3)), int(cap.get(4))))  # 30 FPS

        while streaming_active and not stop_video_thread.is_set():
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame.")
                break

            video_writer.write(frame)

        if video_writer:
            video_writer.release()

        cap.release()
        if os.path.exists(filename):
            blob = bucket.blob(filename)
            blob.upload_from_filename(filename)
            print(f"Video uploaded to gs://{bucket_name}/{filename}")
            os.remove(filename)  # Clean up local file

    except Exception as e:
        print(f"Video capture/upload error: {e}")

    finally:
        cap.release()


def callback(message: pubsub_v1.subscriber.message.Message):
    """Callback function for Pub/Sub messages."""
    process_message(message)


def main():
    """Main function to start Pub/Sub subscriber."""
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for messages on {subscription_path}...")

    try:
        streaming_pull_future.result()  # Blocks indefinitely until a signal is received.
    except KeyboardInterrupt:
        print("Stopping subscriber...")
        streaming_pull_future.cancel()
        streaming_pull_future.result()  # Block until the shutdown is complete.
    finally:
        print("Subscriber stopped.")


if __name__ == "__main__":
    main()
