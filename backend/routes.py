import os
import logging

import datetime
from flask import Blueprint, request, jsonify
from services.firebase_service import FirestoreService
from services.pubsub_service import PubSubService
import config as cfg

# Create a blueprint to reference
api_blueprint = Blueprint('api', __name__)

# Register logger
logger = logging.getLogger(__name__)

# Initialize services
FIRESTORE_SERVICE = FirestoreService(cfg.FIRESTORE_DATABASE_ID)
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
            "stationId": station_id,
            "recordingsWithFeedback": [],
        }

        game_id = FIRESTORE_SERVICE.create_doc(
            collection_name=cfg.GAME_SESSIONS_COLLECTION_NAME,
            data=game_session_data
        )

        # Send start recording message to camera modules (Pub/Sub)
        if game_id:
            topic_id = cfg.PUBSUB_TOPIC_ID.format(station_id=station_id)
            message = {
                "command": "start-game",
                "gameId": game_id,
            }
            PUBSUB_SERVICE.publish_message(cfg.GOOGLE_CLOUD_PROJECT_ID, topic_id, message)

        return jsonify({'gameId': game_id})


@api_blueprint.route("/resume_game", methods=['POST'])
def resume_game():
    if request.method == 'POST':
        received_data = request.get_json()
        station_id = received_data['stationId']
        game_id = received_data['gameId']

        if game_id:
            # Send start recording message to camera modules (Pub/Sub)
            topic_id = cfg.PUBSUB_TOPIC_ID.format(station_id=station_id)
            message = {
                "command": "start-game",
                "gameId": game_id,
            }
            PUBSUB_SERVICE.publish_message(cfg.GOOGLE_CLOUD_PROJECT_ID, topic_id, message)

        return jsonify(message)


@api_blueprint.route("/cancel_game", methods=['POST'])
def cancel_game():
    if request.method == 'POST':
        received_data = request.get_json()
        station_id = received_data['stationId']
        game_id = received_data['gameId']

        # Update gameStatus as "cancelling" in the game sessions database (Firestore)
        FIRESTORE_SERVICE.update_fields(
            collection_name=cfg.GAME_SESSIONS_COLLECTION_NAME,
            document_id=game_id,
            field_value_dict={
                "gameStatus": "cancelling"
            },
        )

        # Send cancel recording message to camera modules (Pub/Sub)
        topic_id = cfg.PUBSUB_TOPIC_ID.format(station_id=station_id)
        message = {
            "command": "cancel-game",
            "gameId": game_id,
        }
        PUBSUB_SERVICE.publish_message(
            project_id=cfg.GOOGLE_CLOUD_PROJECT_ID,
            topic_id=topic_id,
            message=message
        )

        return jsonify({'gameId': game_id})


@api_blueprint.route("/finish_game", methods=['POST'])
def clear_game():
    if request.method == 'POST':
        received_data = request.get_json()
        station_id = received_data['stationId']
        game_id = received_data['gameId']

        FIRESTORE_SERVICE.update_fields(
            collection_name=cfg.GAME_SESSIONS_COLLECTION_NAME,
            document_id=game_id,
            field_value_dict={
                "gameStatus": "completed"
            },
        )

        FIRESTORE_SERVICE.update_fields(
            collection_name=cfg.STATION_INFO_COLLECTION_NAME,
            document_id=f"station{station_id}",
            field_value_dict={
                "gameId": "",
                "isRunning": False,
                "replayVideo": "",
                "geminiAnalysis": "",
            }
        )

        return jsonify({'message': "ok"})
