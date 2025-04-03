import logging
import threading
import os
from google.cloud import storage

log = logging.getLogger(__name__)


class GCSUploader:
    """Handles GCS uploads asynchronously."""

    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.storage_client = None
        self.bucket = None
        try:
            self.storage_client = storage.Client()
            self.bucket = self.storage_client.get_bucket(bucket_name)
            log.info(f"GCS Uploader targeting bucket: gs://{bucket_name}")
        except Exception as e:
            log.error(f"Failed to initialize GCS Uploader for '{bucket_name}': {e}")

    def _upload_task(self, local_path: str, blob_name: str,  make_public: bool, delete_local: bool):
        """Upload logic run in thread."""
        if not self.bucket or not os.path.exists(local_path):
            return
        gcs_video_uri = f"gs://{self.bucket_name}/{blob_name}"
        log.info(f"Uploading: {local_path} -> {gcs_video_uri}")
        try:
            blob = self.bucket.blob(blob_name)
            blob.upload_from_filename(local_path, timeout=300)

            if make_public:
                blob.make_public()
                log.info(f"File is publicly available at: {blob.public_url}")

            log.info(f"Upload successful: {gcs_video_uri}")

            if delete_local:
                os.remove(local_path)
                log.info(f"Deleted local: {local_path}")

        except Exception as e:
            log.error(f"Upload failed for {local_path}: {e}")

    def upload_file(self, local_path: str, blob_name: str, make_public: bool = True, delete_local: bool = False,
                    upload_async: bool = True):
        """Starts upload in a background thread."""
        if not self.bucket:
            return log.error("GCS Bucket not ready, cannot upload.")

        if upload_async:
            threading.Thread(target=self._upload_task, args=(local_path, blob_name, make_public, delete_local),
                             name=f"Upload-{os.path.basename(local_path)}", daemon=True).start()
        else:
            self._upload_task(local_path, blob_name, make_public, delete_local)

    def is_ready(self) -> bool:
        return self.bucket is not None
