# firestore_utils.py (or your chosen filename)
import logging
from google.cloud import firestore
from google.cloud.exceptions import GoogleCloudError, NotFound
from google.auth.exceptions import DefaultCredentialsError

log = logging.getLogger(__name__)


class FirestoreUpdater:
    """
    Handles initialization of and updates to Firestore documents.
    """
    def __init__(self, project_id: str, database_id: str = "(default)"):
        """
        Initializes the Firestore client.

        Args:
            project_id: Your Google Cloud project ID.
            database_id: The Firestore database ID (defaults to '(default)').
        """
        self.project_id = project_id
        self.database_id = database_id
        self.db_client: firestore.Client | None = None
        self._ready = False  # Flag to indicate successful initialization

        try:
            self.db_client = firestore.Client(project=self.project_id, database=self.database_id)
            self._ready = True
            log.info(f"Firestore client initialized for project: '{self.project_id}', database: '{self.database_id}'")
        except DefaultCredentialsError as e:
            log.critical(f"Firestore Authentication error: {e}")
            raise RuntimeError("Firestore Authentication failed") from e
        except Exception as e:
            log.critical(f"Failed to initialize Firestore client for project '{self.project_id}': {e}",
                         exc_info=True)
            raise RuntimeError("Firestore client initialization failed") from e

    def is_ready(self) -> bool:
        """Returns True if the Firestore client initialized successfully."""
        return self._ready and self.db_client is not None

    def update_document(self, collection_name: str, document_id: str, field_updates: dict) -> bool:
        """
        Updates one or more fields in a specific Firestore document.

        Args:
            collection_name: The ID of the collection.
            document_id: The ID of the document to update.
            field_updates: A dictionary where keys are field names (can use dot notation
                           for nested fields, e.g., 'details.status') and values are the new values.

        Returns:
            True if update is successful, False otherwise.
        """
        if not self.is_ready():
            log.error("Firestore client is not ready or initialized. Cannot update document.")
            return False

        log.info(f"Updating Firestore document: {collection_name}/{document_id}")
        try:
            doc_ref = self.db_client.collection(collection_name).document(document_id)
            doc_ref.update(field_updates)
            log.info(f"Successfully updated Firestore document: {collection_name}/{document_id} with: {field_updates}")
            return True
        except NotFound:
             log.error(f"Firestore document not found: {collection_name}/{document_id}. Cannot update.")
             return False
        except GoogleCloudError as e:
            log.error(f"Firestore update failed for {collection_name}/{document_id}: {e}")
            return False
        except Exception as e:
            log.error(f"Unexpected error during Firestore update for {collection_name}/{document_id}: {e}",
                      exc_info=True)
            return False
