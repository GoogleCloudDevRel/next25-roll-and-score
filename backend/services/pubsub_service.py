import json
import logging

from google.cloud import pubsub_v1

# Register logger
logger = logging.getLogger(__name__)


class PubSubService:
    _instance = None  # Singleton instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            logger.info("Creating new PubSubService instance")
            cls._instance = super().__new__(cls)
            cls._instance.publisher = None
        else:
            logger.info("Using existing PubSubService instance")
        return cls._instance

    def __init__(self):
        if self.publisher is None:
            try:
                self.publisher = pubsub_v1.PublisherClient()
            except Exception as e:
                logger.error(f"Error initializing PubSub Client: {e}")
                self.publisher = None  # to prevent further errors, set db to none.
        else:
            logger.info(f"{self.__class__.__name__}: __init__ skipped because instance already initialized")

    def publish_message(self, project_id, topic_id, message):
        """
        Publishes a JSON message to a Pub/Sub topic synchronously.
        Synchronous completion is crucial because subsequent tasks depend on it.
        """
        topic_path = self.publisher.topic_path(project_id, topic_id)
        message_json = json.dumps(message).encode("utf-8")

        try:
            future = self.publisher.publish(topic_path, message_json)
            message_id = future.result()
            logger.info(f"Published {message_json} to {topic_path}. Message ID: {message_id}")
        except Exception as e:
            logger.error(f"Publishing {message_json} to {topic_path} raised an exception: {e}")
            raise e
