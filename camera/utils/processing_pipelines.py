import json
import logging
import time
from typing import Tuple, Dict, List, Optional, Callable

import cv2
import numpy as np

import config as cfg

log = logging.getLogger(__name__)

# Type Hinting
HoleData = Tuple[int, int, int, int, int]
HolesDict = Dict[str, HoleData]
BallCenter = Optional[Tuple[int, int]]
ScoreEvent = Tuple[float, int, str]


# --- Base Processor Definition ---
class BaseProcessor:
    """Base class for frame processors."""

    def process(self, frame: np.ndarray) -> np.ndarray: return frame

    def reset(self): pass

    def get_summary(self) -> Optional[Dict]: return None


# --- SkeeBall Helper Functions ---
def _load_holes_config_from_json(json_path: str) -> HolesDict:
    """Loads hole configurations from JSON."""
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        holes_config: HolesDict = {}
        for i, zone in enumerate(data.get('score_zones', [])):
            label = str(zone.get('label', f'zone_{i}'))
            bbox = zone.get('bbox')
            score = int(zone.get('score', label))
            if isinstance(bbox, list) and len(bbox) == 4:
                x_min, y_min, x_max, y_max = map(int, bbox)
                holes_config[f"{label}_{i}"] = (x_min, y_min, x_max, y_max, score)
            else:
                log.warning(f"Skipping invalid zone format: {zone}")
        log.info(f"Loaded {len(holes_config)} score zones from '{json_path}'.")
        return holes_config
    except Exception as e:
        log.error(f"Failed to load hole config '{json_path}': {e}")
        return {}


def _detect_ball(frame: np.ndarray, lower_hsv: np.ndarray, upper_hsv: np.ndarray,
                 min_area: int, max_area: int, min_circularity: float,
                 kernel_size: Tuple[int, int], iterations: int
                 ) -> Tuple[BallCenter, Optional[np.ndarray]]:
    """Detects the best ball candidate."""
    try:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
        kernel = np.ones(kernel_size, np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=iterations)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=iterations)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    except Exception as e:
        log.debug(f"OpenCV error during ball detection pre-processing: {e}")
        return None, None

    best_ball_contour: Optional[np.ndarray] = None
    max_valid_area = 0
    for contour in contours:
        area = cv2.contourArea(contour)
        if min_area <= area <= max_area:
            perimeter = cv2.arcLength(contour, True)
            if perimeter > 1e-6:
                circularity = (4 * np.pi * area) / (perimeter * perimeter)
                if circularity >= min_circularity and area > max_valid_area:
                    max_valid_area = area
                    best_ball_contour = contour
    if best_ball_contour is not None:
        M = cv2.moments(best_ball_contour)
        if abs(M["m00"]) > 1e-6:
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            return center, best_ball_contour
    return None, best_ball_contour


def _does_ball_overlap_hole(ball_contour: np.ndarray, hole_roi: Tuple[int, int, int, int],
                            frame_shape: Tuple[int, int]) -> bool:
    """Checks for intersection using masks."""
    try:
        h, w = frame_shape
        ball_mask = np.zeros((h, w), dtype=np.uint8)
        cv2.drawContours(ball_mask, [ball_contour], -1, 255, cv2.FILLED)
        hole_mask = np.zeros((h, w), dtype=np.uint8)
        x_min, y_min, x_max, y_max = hole_roi
        x_min, y_min = max(0, x_min), max(0, y_min)
        x_max, y_max = min(w, x_max), min(h, y_max)
        cv2.rectangle(hole_mask, (x_min, y_min), (x_max, y_max), 255, cv2.FILLED)
        return cv2.countNonZero(cv2.bitwise_and(ball_mask, hole_mask)) > 0
    except Exception as e:
        log.debug(f"Error during overlap check: {e}")
        return False


def _get_overlapping_hole(ball_contour: np.ndarray, holes: HolesDict, frame_shape: Tuple[int, int]
                          ) -> Optional[Tuple[str, int]]:
    for hole_id, (*roi, score) in holes.items():
        if _does_ball_overlap_hole(ball_contour, roi, frame_shape): return hole_id, score
    return None


def _draw_skeeball_visualizations(frame: np.ndarray, holes: HolesDict, ball_contour: Optional[np.ndarray],
                                  total_score: int, armed_hole_id: Optional[str]) -> None:
    """Draws overlays onto the frame."""
    h = frame.shape[0]
    roi_clr, armed_clr, ball_clr, text_clr = (0, 255, 0), (0, 255, 255), (0, 255, 255), (255, 255, 255)
    font, thick = cv2.FONT_HERSHEY_SIMPLEX, 2
    for hid, (xmin, ymin, xmax, ymax, sc) in holes.items():
        clr = armed_clr if hid == armed_hole_id else roi_clr
        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), clr, thick)
        cv2.putText(frame, str(sc), (xmin + 5, ymin + 30), font, 0.7, clr, thick, cv2.LINE_AA)
    if ball_contour is not None: cv2.drawContours(frame, [ball_contour], -1, ball_clr, cv2.FILLED)
    cv2.putText(frame, f"Score: {total_score}", (10, h - 20), font, 0.9, text_clr, thick, cv2.LINE_AA)


# --- SkeeBall Score Tracking Processor ---
class ScoreTrackingProcessor(BaseProcessor):
    """Processes frames for skee-ball scoring."""

    def __init__(self, score_callback: Optional[Callable[[ScoreEvent], None]] = None, **kwargs):
        self.score_callback = score_callback
        self.holes_config = _load_holes_config_from_json(cfg.SKEEBALL_SCORE_ZONES_JSON_PATH)
        if not self.holes_config: raise ValueError("Hole config missing/invalid.")
        # Store config parameters
        self.hsv_lower = cfg.SKEEBALL_LOWER_HSV
        self.hsv_upper = cfg.SKEEBALL_UPPER_HSV
        self.min_area = cfg.SKEEBALL_MIN_BALL_AREA
        self.max_area = cfg.SKEEBALL_MAX_BALL_AREA
        self.min_circ = cfg.SKEEBALL_MIN_CIRCULARITY
        self.k_size = cfg.SKEEBALL_MORPH_KERNEL_SIZE
        self.iters = cfg.SKEEBALL_MORPH_ITERATIONS
        self.req_pres = cfg.SKEEBALL_REQUIRED_PRESENCE_FRAMES
        self.timeout = cfg.SKEEBALL_SCORE_TIMEOUT_SECONDS
        self.grace = cfg.SKEEBALL_DISAPPEARANCE_GRACE_FRAMES
        self.reset()

    def reset(self):
        """Resets scoring state."""
        self.total_score: int = 0
        self.scored_events: List[ScoreEvent] = []
        self.presence_cnt: Dict[str, int] = {h: 0 for h in self.holes_config}
        self.armed: Optional[Dict] = None
        self.missing_frames: int = 0
        self.last_score_t: Dict[str, float] = {}
        self.start_time = time.monotonic()

    def process(self, frame: np.ndarray) -> np.ndarray:
        """Applies skee-ball logic and visualization."""
        current_time = time.monotonic()
        elapsed = current_time - self.start_time
        shape = frame.shape[:2]
        center, contour = _detect_ball(frame, self.hsv_lower, self.hsv_upper, self.min_area,
                                       self.max_area, self.min_circ, self.k_size, self.iters)
        detected = contour is not None
        overlap_id, overlap_score = None, None
        if detected:
            res = _get_overlapping_hole(contour, self.holes_config, shape)
            if res: overlap_id, overlap_score = res

        # Arming/Disarming State Machine
        if not self.armed:
            if overlap_id:
                self.presence_cnt[overlap_id] += 1
                if self.presence_cnt[overlap_id] >= self.req_pres:
                    self.armed = {'id': overlap_id, 'score': overlap_score}
                    self.missing_frames = 0
            for hid in self.holes_config:
                if hid != overlap_id: self.presence_cnt[hid] = 0
        else:  # Armed
            if detected:
                if overlap_id == self.armed['id']:
                    self.missing_frames = 0
                else:
                    self.armed = None
                    self.presence_cnt = {h: 0 for h in self.holes_config}
            else:
                self.missing_frames += 1

        # Scoring
        if self.armed and self.missing_frames > self.grace:
            hole_id, score = self.armed['id'], self.armed['score']
            if current_time - self.last_score_t.get(hole_id, -self.timeout * 2) > self.timeout:
                self.total_score += score
                event = (elapsed, score, hole_id)
                self.scored_events.append(event)
                self.last_score_t[hole_id] = current_time
                log.info(f"*** SCORE! Hole:{hole_id} (+{score}), Total:{self.total_score} ***")
                if self.score_callback:
                    try:
                        self.score_callback(event)
                    except Exception as e:
                        log.error(f"Callback error: {e}")
            # Disarm after check
            self.armed = None
            self.missing_frames = 0
            self.presence_cnt = {h: 0 for h in self.holes_config}

        # Visualize
        out_frame = frame.copy()
        _draw_skeeball_visualizations(out_frame, self.holes_config, contour, self.total_score,
                                      self.armed['id'] if self.armed else None)
        return out_frame

    def get_summary(self) -> Optional[Dict]:
        return {"final_score": self.total_score, "scored_events": self.scored_events}


# --- Processor Getter ---
def get_processor(key: Optional[str], score_callback: Optional[Callable[[ScoreEvent], None]] = None, **kwargs) -> \
        Optional[BaseProcessor]:
    """Returns the requested processor instance."""
    if key:
        if key == "score_tracker":
            try:
                return ScoreTrackingProcessor(score_callback=score_callback)
            except Exception as e:
                log.error(f"Failed to create ScoreTrackingProcessor: {e}")
        else:
            log.warning(f"No associated processor for the processing key: {key}")
