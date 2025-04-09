import logging
from google.cloud import pubsub_v1

log = logging.getLogger(__name__)


class PubSubPublisher:
    """Handles publishing messages to Pub/Sub."""

    def __init__(self, project_id: str, topic_id: str):
        self.publisher_client = pubsub_v1.PublisherClient()
        self.topic_path = self.publisher_client.topic_path(project_id, topic_id)
        log.info(f"Pub/Sub Publisher targeting topic: {self.topic_path}")

    def publish_message(self, message_data: bytes, **kwargs):
        """Publishes a message."""
        if not isinstance(message_data, bytes):
            message_data = str(message_data).encode('utf-8')
        try:
            future = self.publisher_client.publish(self.topic_path, message_data, **kwargs)
            message_id = future.result(timeout=10)
            log.info(f"Published message ID {message_id}")
            return True
        except Exception as e:
            log.error(f"Failed to publish message: {e}")
            return False

    def is_ready(self) -> bool:
        return self.publisher_client is not None

    def close(self):
        if self.publisher_client: self.publisher_client.stop()
