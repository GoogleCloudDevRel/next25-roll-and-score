import os
import json
from google.cloud import pubsub_v1


def publish_message(message_data):
    """Publishes a JSON message to a Pub/Sub topic."""

    project_id = os.environ['PROJECT_ID']
    topic_id = os.environ['PUBSUB_TOPIC_ID']

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    # Convert the dictionary to a JSON string and then to bytes
    message_json = json.dumps(message_data).encode("utf-8")

    future = publisher.publish(topic_path, message_json)
    try:
        print(f"Published message ID: {future.result()}")
    except Exception as e:
        print(f"Publishing {message_json} to {topic_path} raised an exception: {e}")

    print(f"Published message to {topic_path}.")


if __name__ == "__main__":
    msg = [
        {"commend": "start-recording"},
        {"commend": "stop-recording"},
    ]
    publish_message(msg[1])
