import os
import logging

import datetime
from flask import Blueprint, request, jsonify
from services.firebase_service import FirestoreService
from services.pubsub_service import PubSubService

# Create a blueprint to reference
api_blueprint = Blueprint('api', __name__)

# Register logger
logger = logging.getLogger(__name__)

# Retrieve from the environment variables
GC_PROJECT_ID = os.environ['GC_PROJECT_ID']
FS_DATABASE_ID = os.environ['FS_DATABASE_ID']
FS_COLLECTION_NAME = os.environ["FS_COLLECTION_NAME"]

# Initialize services
FIRESTORE_SERVICE = FirestoreService(FS_DATABASE_ID)
PUBSUB_SERVICE = PubSubService()

@api_blueprint.route("/health", methods=['GET'])
def health():
    return jsonify({"status": "OK"}), 200


@api_blueprint.route("/start_game", methods=['POST'])
def start_game():
    if request.method == 'POST':
        received_data = request.get_json()
        station_id = received_data['stationId']
        now = datetime.datetime.now(datetime.timezone.utc)  # Ensure UTC Time.

        # Create a new entry in the game sessions database (Firestore)
        game_session_data = {
            "scores": [],
            "totalScore": 0,
            "gameStatus": "starting",
            "startDateTime": now,
            "endDateTime": None,
            "stationId": station_id
        }

        game_id = FIRESTORE_SERVICE.create_doc(
            collection_name=FS_COLLECTION_NAME,
            data=game_session_data
        )

        # Send start recording message to camera modules (Pub/Sub)
        if game_id:
            topic_id = f"station{station_id:02d}"
            message = {
                "command": "start-recording",
                "gameId": game_id,
            }
            PUBSUB_SERVICE.publish_message(GC_PROJECT_ID, topic_id, message)

        return jsonify({'gameId': game_id})


@api_blueprint.route("/end_game", methods=['POST'])
def end_game():
    if request.method == 'POST':
        received_data = request.get_json()
        station_id = received_data['stationId']
        game_id = received_data['gameId']

        # Send stop recording message to camera modules (Pub/Sub)
        topic_id = f"station{station_id:02d}"
        message = {
            "command": "stop-recording",
            "gameId": game_id,
        }
        PUBSUB_SERVICE.publish_message(
            project_id=GC_PROJECT_ID,
            topic_id=topic_id,
            message=message
        )

        # Update gameStatus as "cancelled" in the game sessions database (Firestore)
        field_name = "gameStatus"
        field_value = "stopping"
        FIRESTORE_SERVICE.update_field(
            collection_name=FS_COLLECTION_NAME,
            document_id=game_id,
            field_name=field_name,
            field_value=field_value
        )

        return jsonify({"gameId": game_id, field_name: field_value})


@api_blueprint.route("/leaderboard", methods=['GET'])
def leaderboard():
    top_5_scores = FIRESTORE_SERVICE.get_top_n_by_score(
        collection_name=FS_COLLECTION_NAME,
        score_field="totalScore",
        n=5
    )

    return jsonify({"highScores": top_5_scores})


@api_blueprint.route("/get_scores", methods=['POST'])
def get_scores_array():
    if request.method == 'POST':
        received_data = request.get_json()
        game_id = received_data['gameId']
        scores_field_name = "Scores"

        current_scores_array = FIRESTORE_SERVICE.get_field(
            collection_name=FS_COLLECTION_NAME,
            document_id=game_id,
            field_name=scores_field_name
        )

        return jsonify({"scores", current_scores_array})


@api_blueprint.route("/add_score", methods=['POST'])
def add_score():
    if request.method == 'POST':
        received_data = request.get_json()
        game_id = received_data['gameId']
        new_score = received_data['score']
        scores_field_name = "Scores"

        # Insert a score to the Scores array in provide game session (Firestore)
        FIRESTORE_SERVICE.add_item_to_list(
            collection_name=FS_COLLECTION_NAME,
            document_id=game_id,
            list_field_name=scores_field_name,
            item=new_score
        )

        return jsonify({"message": f"Added {new_score} to Scores array from {game_id}"})
