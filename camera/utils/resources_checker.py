import logging

# --- Google Cloud Imports ---
from google.cloud import pubsub_v1, storage, firestore
from google.cloud.exceptions import NotFound, Conflict, GoogleCloudError
from google.auth.exceptions import DefaultCredentialsError

from firebase_admin import firestore

log = logging.getLogger(__name__)


def check_create_gcs_bucket(project_id: str, bucket_name: str, location: str = 'US'):
    """
    Checks if a GCS bucket exists, creates it if not.
    Raises RuntimeError on failure.
    """
    log.info(f"Checking GCS Bucket '{bucket_name}'...")
    try:
        storage_client = storage.Client(project=project_id)
        try:
            storage_client.get_bucket(bucket_name)
            log.info(f"GCS Bucket '{bucket_name}' already exists.")
        except NotFound:
            log.warning(f"GCS Bucket '{bucket_name}' not found. Attempting to create in location '{location}'...")
            try:
                storage_client.create_bucket(bucket_name, location=location)
                log.info(f"Successfully created GCS Bucket '{bucket_name}'.")
            except Conflict:
                log.warning(f"GCS Bucket '{bucket_name}' already exists (likely created recently).")
            except GoogleCloudError as e:
                log.error(f"Failed to create GCS bucket '{bucket_name}': {e}. Check permissions (Storage Admin?).")
                raise RuntimeError(f"Bucket creation failed for {bucket_name}: {e}") from e
    except DefaultCredentialsError as e:
        log.critical(f"GCS Authentication error: {e}")
        raise RuntimeError("GCS Authentication failed") from e
    except Exception as e:
        log.critical(f"Unexpected error checking/creating GCS bucket '{bucket_name}': {e}", exc_info=True)
        raise # Re-raise unexpected errors


def check_create_pubsub_topic(project_id: str, topic_id: str) -> str:
    """
    Checks if a Pub/Sub topic exists, creates it if not.
    Returns the topic path on success.
    Raises RuntimeError on failure.
    """
    log.info(f"Checking Pub/Sub Topic '{topic_id}'...")
    topic_path = None
    try:
        publisher_client = pubsub_v1.PublisherClient()
        topic_path = publisher_client.topic_path(project_id, topic_id)
        try:
            publisher_client.get_topic(request={"topic": topic_path})
            log.info(f"Pub/Sub Topic '{topic_id}' already exists.")
        except NotFound:
            log.warning(f"Pub/Sub Topic '{topic_id}' not found. Attempting to create...")
            try:
                publisher_client.create_topic(request={"name": topic_path})
                log.info(f"Successfully created Pub/Sub Topic '{topic_id}'.")
            except Conflict:
                log.warning(f"Pub/Sub Topic '{topic_id}' already exists (likely created recently).")
            except GoogleCloudError as e:
                log.error(f"Failed to create Pub/Sub topic '{topic_id}': {e}. Check permissions (Pub/Sub Admin?).")
                raise RuntimeError(f"Topic creation failed for {topic_id}: {e}") from e
        return topic_path # Return path if successful
    except DefaultCredentialsError as e:
        log.critical(f"Pub/Sub Authentication error: {e}")
        raise RuntimeError("Pub/Sub Authentication failed") from e
    except Exception as e:
        log.critical(f"Unexpected error checking/creating Pub/Sub topic '{topic_id}': {e}", exc_info=True)
        raise # Re-raise unexpected errors


def check_create_pubsub_subscription(project_id: str, subscription_id: str, topic_path: str):
    """
    Checks if a Pub/Sub subscription exists, creates it if not for the given topic path.
    Raises RuntimeError on failure.
    """
    log.info(f"Checking Pub/Sub Subscription '{subscription_id}'...")
    if not topic_path:
        raise ValueError("Cannot check/create subscription without a valid topic_path.")

    try:
        subscriber_client = pubsub_v1.SubscriberClient()
        subscription_path = subscriber_client.subscription_path(project_id, subscription_id)
        try:
            subscriber_client.get_subscription(request={"subscription": subscription_path})
            log.info(f"Pub/Sub Subscription '{subscription_id}' already exists.")
        except NotFound:
            topic_id = topic_path.split('/')[-1] # Extract topic_id for logging
            log.warning(f"Pub/Sub Subscription '{subscription_id}' not found. Attempting to create for topic '{topic_id}'...")
            try:
                subscriber_client.create_subscription(request={
                    "name": subscription_path,
                    "topic": topic_path,
                    # "ack_deadline_seconds": 10, # Default, customize if needed
                })
                log.info(f"Successfully created Pub/Sub Subscription '{subscription_id}'.")
            except Conflict:
                log.warning(f"Pub/Sub Subscription '{subscription_id}' already exists (likely created recently).")
            except GoogleCloudError as e:
                log.error(
                    f"Failed to create subscription '{subscription_id}': {e}. "
                    f"Check permissions (Pub/Sub Admin?) and ensure topic exists.")
                raise RuntimeError(f"Subscription creation failed for {subscription_id}: {e}") from e
    except DefaultCredentialsError as e:
        log.critical(f"Pub/Sub Authentication error: {e}")
        raise RuntimeError("Pub/Sub Authentication failed") from e
    except Exception as e:
        log.critical(f"Unexpected error checking/creating Pub/Sub subscription '{subscription_id}': {e}", exc_info=True)
        raise # Re-raise unexpected errors


def check_firestore_access(project_id: str, database_id: str):
    """
    Attempts to initialize a Firestore client to check access/API enablement.
    Raises RuntimeError on failure.
    """
    log.info(f"Checking Firestore access for project '{project_id}'...")
    try:
        # Initialize client - this implicitly checks API enablement and basic auth
        db = firestore.Client(project=project_id, database=database_id)
        log.info("Firestore access verified successfully.")
    except DefaultCredentialsError as e:
        log.critical(f"Firestore Authentication error during check: {e}")
        raise RuntimeError("Firestore Authentication failed during check") from e
    except Exception as e:
        # Catch other potential exceptions during initialization
        log.critical(f"Failed to verify Firestore access for project '{project_id}': {e}", exc_info=True)
        raise RuntimeError("Firestore access check failed") from e


def ensure_gcp_resources(project_id: str, topic_id: str, subscription_id: str, bucket_name: str,
                         bucket_location: str, database_id: str):
    """
    Orchestrates the checking and creation of required GCS and Pub/Sub resources.
    Calls individual check/create functions.
    Raises RuntimeError if any step fails.
    """
    log.info("----- Ensuring required GCP resources -----")
    try:
        # Check/Create GCS Bucket
        check_create_gcs_bucket(project_id, bucket_name, bucket_location)

        # Check/Create Pub/Sub Topic (and get path)
        topic_path = check_create_pubsub_topic(project_id, topic_id)

        # Check/Create Pub/Sub Subscription (using topic path)
        check_create_pubsub_subscription(project_id, subscription_id, topic_path)

        # Check firestore access
        check_firestore_access(project_id, database_id)

        log.info("----- GCP resource check/creation complete. -----")
    except Exception as e:
        log.critical(f"Failed to ensure all GCP resources: {e}", exc_info=False) # Log specific error from raised exception
        # Re-raise the original exception to signal failure to the caller
        raise
