# pubsub_listener.py
import logging
import threading
import time
from google.cloud import pubsub_v1
from typing import Optional, Callable

log = logging.getLogger(__name__)


class PubSubListener:
    """Listens to Pub/Sub subscription and executes a callback."""

    def __init__(self, project_id: str, sub_id: str, callback: Callable[[str], None]):
        self.callback = callback
        self.subscriber = None
        self.sub_path = None
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._future = None
        try:
            self.subscriber = pubsub_v1.SubscriberClient()
            self.sub_path = self.subscriber.subscription_path(project_id, sub_id)
            log.info(f"Pub/Sub Listener targeting subscription: {self.sub_path}")
        except Exception as e:
            log.error(f"Failed to init Pub/Sub Listener: {e}")

    def _message_handler(self, message: pubsub_v1.subscriber.message.Message):
        """Handles incoming messages."""
        try:
            data = message.data.decode("utf-8").strip()
            log.info(f"Received Pub/Sub message: {data[:100]}{'...' if len(data) > 100 else ''}")  # Log truncated data
            self.callback(data)
            message.ack()
        except Exception as e:
            log.error(f"Error processing msg {message.message_id}: {e}")

    def listen(self):
        """Starts listening thread."""
        if not self.is_ready() or (self._thread and self._thread.is_alive()): return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name="PubSubListen", daemon=True)
        self._thread.start()

    def _run(self):
        """Manages streaming pull connection."""
        log.info(f"Listener starting for {self.sub_path}")
        while not self._stop.is_set():
            try:
                self._future = self.subscriber.subscribe(self.sub_path, self._message_handler)
                self._future.result()  # Blocks
            except Exception as e:  # Catch broad exceptions in demo
                log.warning(f"Pub/Sub listener error ({type(e).__name__}), retrying in 5s...")
                if self._future: self._future.cancel()
            if not self._stop.is_set(): time.sleep(5)
        log.info("Listener run loop finished.")

    def stop(self):
        """Signals listener thread to stop."""
        if self._stop.is_set(): return
        log.info("Stopping Pub/Sub listener...")
        self._stop.set()
        if self._future: self._future.cancel()

    def is_ready(self) -> bool:
        return self.subscriber is not None
