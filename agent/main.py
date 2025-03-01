import os
import sys
import signal
import logging
from google.cloud import pubsub_v1
from opentelemetry.metrics import get_meter_provider, Meter
from opentelemetry.sdk.metrics import MeterProvider
import yaml
import asyncio


# Configure logging
logging.basicConfig(
    filename="skeeball_agent.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Load configuration from YAML file
CONFIG_FILE = "config.yaml"  # Name of your config file

try:
    with open(CONFIG_FILE, "r") as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    logging.error(f"Configuration file '{CONFIG_FILE}' not found.")
    sys.exit(1)
except yaml.YAMLError as e:
    logging.exception(f"Error parsing YAML: {e}")
    sys.exit(1)

# Access configuration values (examples)
PROJECT_ID = config.get("project_id")
SUBSCRIPTION_ID = config.get("subscription_id")
SOME_OTHER_SETTING = config.get("some_other_setting", "default_value")  # Default value

# Initialize OpenTelemetry Meter
meter_provider = MeterProvider()
meter = meter_provider.get_meter("skeeball-agent")
message_counter = meter.create_counter(
    name="messages_processed", description="Number of messages processed"
)


def process_message(message):  # Separate function for message processing
    """Processes a Pub/Sub message."""
    message_counter.add(1)
    try:
        data = message.data.decode("utf-8")
        logging.info(f"Received message: {data}")

        if data == "start":
            logging.info("Starting something...")
            # Your start logic here
        elif data == "stop":
            logging.info("Stopping something...")
            # Your stop logic here
        else:
            logging.warning(f"Unknown message received: {data}")

        message.ack()  # Acknowledge *after* successful processing

    except Exception as e:
        logging.exception(f"Error processing message: {e}")
        message.nack()  # Negative acknowledge on error


def subscribe_to_pubsub():
    """Subscribes to Pub/Sub and processes messages."""

    if not PROJECT_ID or not SUBSCRIPTION_ID:
        logging.error("PROJECT_ID and SUBSCRIPTION_ID must be set.")
        sys.exit(1)  # Exit with error status code

    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)

    try:
        future = subscriber.subscribe(subscription_path, callback=process_message)
        logging.info(f"Listening on subscription {subscription_path}...")
        future.result()  # Blocks indefinitely

    except Exception as e:
        logging.exception(f"Error subscribing to Pub/Sub: {e}")
        sys.exit(1)  # Exit with error code


def signal_handler(signum, frame):
    logging.info("Skeeball agent stopping...")
    sys.exit(0)  # Exit gracefully


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    logging.info("Skeeball agent starting...")
    subscribe_to_pubsub()
