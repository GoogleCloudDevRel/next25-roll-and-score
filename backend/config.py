import os

GOOGLE_CLOUD_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID", "next-25-roll-and-score")
GOOGLE_CLOUD_REGION = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
FIRESTORE_DATABASE_ID = os.getenv("FIRESTORE_DATABASE_ID", "roll-and-score")
GAME_SESSIONS_COLLECTION_NAME = os.getenv("GAME_SESSIONS_COLLECTION", "game-sessions")
STATION_INFO_COLLECTION_NAME = os.getenv("STATION_INFO_COLLECTION_NAME", "station-info")
PUBSUB_TOPIC_ID = os.getenv("PUBSUB_TOPIC_ID", "station{station_id}-pub")
