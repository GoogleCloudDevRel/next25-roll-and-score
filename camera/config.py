import os
import logging
import numpy as np

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
log = logging.getLogger(__name__)

# --- STATION Configuration ---
STATION_ID = os.environ["STATION_ID"]

# --- Google Cloud Configuration ---
CHECK_GOOGLE_CLOUD_RESOURCES = False
GOOGLE_CLOUD_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID", "next-25-roll-and-score")
GOOGLE_CLOUD_REGION = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
PUBSUB_TOPIC_ID = os.getenv("PUBSUB_TOPIC_ID", f"{STATION_ID}-pub")
PUBSUB_SUBSCRIPTION_ID = os.getenv("PUBSUB_SUBSCRIPTION_ID", f"{STATION_ID}-sub")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", f"{STATION_ID}-recordings")
FIRESTORE_DATABASE_ID = os.getenv("FIRESTORE_DATABASE_ID", "roll-and-score")
GAME_SESSIONS_COLLECTION_NAME = os.getenv("GAME_SESSIONS_COLLECTION", "game-sessions")
STATION_STATUSES_COLLECTION_NAME = os.getenv("STATION_STATUS_COLLECTION_NAME", "station-statuses")

# --- Webcam & Recording Configuration ---
# Source either webcam index (0, 1, etc.) or a video path
WEBCAM_CONFIGS = [
    {
        "source": "./scoring_cam1_2.avi",
        "output_filename": "scoreboard_view.mp4",
        "processing_key": "score_tracker"
    },
    {
        "source": "./scoring_cam2_2.avi",
        "output_filename": "lane_view.mp4",
        "processing_key": None
    },
]

OUTPUT_DIR = "./recordings"  # Directory to save recordings locally before upload
VIDEO_FPS = 30.0  # Desired frames per second
VIDEO_RESOLUTION = (640, 480)  # Desired resolution (width, height)

# SkeeBall Tracker Settings
SKEEBALL_SCORE_ZONES_JSON_PATH = 'calibration/score_zones.json'
SKEEBALL_LOWER_HSV = np.array([90, 80, 25])
SKEEBALL_UPPER_HSV = np.array([130, 255, 255])
SKEEBALL_MIN_BALL_AREA = 150
SKEEBALL_MAX_BALL_AREA = 5000
SKEEBALL_MIN_CIRCULARITY = 0.7
SKEEBALL_MORPH_KERNEL_SIZE = (5, 5)
SKEEBALL_MORPH_ITERATIONS = 2
SKEEBALL_REQUIRED_PRESENCE_FRAMES = 2
SKEEBALL_SCORE_TIMEOUT_SECONDS = 1.5
SKEEBALL_DISAPPEARANCE_GRACE_FRAMES = 3

# Game Logic
SCORES_PER_GAME_SESSION = 3  # Trigger stop after this many scores

# Gemini Coach Settings
COACH_SYSTEM_INSTRUCTION = ("You are an experienced skeeball coach. "
                            "Your task is to watch a provided skeeball video and offer concise and engaging feedback.")
COACH_PROMPT_TEMPLATE = """
Instructions:
1. Carefully Watch this videos from a skeeball game: {lane_view_video}
2. Provide feedback in exactly two lines without adding any additional text.
3. The first line should be a fun, engaging message that directly involves the player by comparing *their* throws or 
skill to a superhero (Marvel, DC, or others), designed to make them smile. For example:
    * "Are *you* the Flash? Those balls are lightning fast!"
    * "Is Hawkeye here? Those throws are bullseye every time!"
    * "Feeling like Wonder Woman? That aim is truly heroic!"
    * "Did *you* just channel the power of Thor? Those throws have thunder!"
    * "Are *you* Batman in disguise? Those gadgets must be helping your aim!"
    * "Looks like Spider-Man's got a new skill! Great web-slinging... I mean, ball-rolling!"
    * "Hey Star-Lord, nice moves! Guardians of the Galaxy need your skeeball skills!"
    * "By Grayskull, *you* have the power! Keep those heroic rolls coming!"
4. The second line should offer direct, constructive advice on the player's technique or strategy. For example:
    * "Excellent power, try focusing on a smoother release."
    * "Great accuracy, maintain that consistent stance."
    * "Good effort, try aiming for the higher scoring zones."
    * "Your arm swing is a bit erratic, try a more pendulum-like motion."
    * "Consider a slight adjustment to your throwing angle."
    * "You're doing well, experiment with a little more/less force."
    * "Try leading with your elbow for a more controlled throw."
    * "Remember to follow through completely with your arm."

Your feedback:
"""