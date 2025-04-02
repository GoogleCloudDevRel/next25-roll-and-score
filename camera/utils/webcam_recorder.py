# webcam_recorder.py
import logging
import os
import threading
import time
from typing import Optional, Tuple

import cv2

from .processing_pipelines import BaseProcessor

log = logging.getLogger(__name__)


class WebcamRecorder:
    """Manages video capture and recording for one webcam."""

    def __init__(self, webcam_id: int, output_dir: str, output_filename: str, fps: float,
                 resolution: Tuple[int, int], codec: str = 'mp4v', processor: Optional[BaseProcessor] = None):
        self.webcam_id = webcam_id
        self.output_dir = output_dir
        self.output_filename = output_filename
        self.fps = fps
        self.target_res = resolution
        self.codec = cv2.VideoWriter_fourcc(*codec)
        self.processor = processor
        self.is_recording = False
        self.capture = None
        self.writer_original = None
        self.writer_annotated = None
        self.output_file_original = None
        self.output_file_annotated = None
        self.thread = None
        self._stop = threading.Event()
        self.actual_res = self.target_res
        os.makedirs(self.output_dir, exist_ok=True)

    def _init_capture(self) -> bool:
        """Initializes video capture device."""
        try:
            self.capture = cv2.VideoCapture(self.webcam_id)
            if not self.capture.isOpened(): raise IOError("Cannot open webcam")
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.target_res[0])
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.target_res[1])
            self.capture.set(cv2.CAP_PROP_FPS, self.fps)
            w = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.actual_res = (w, h) if w > 0 and h > 0 else self.target_res
            log.info(f"Webcam {self.webcam_id} opened (Res: {self.actual_res})")
            return True
        except Exception as e:
            log.error(f"Webcam {self.webcam_id} init error: {e}")
            self._release()
            return False

    def start_recording(self) -> bool:
        """Starts recording in a background thread."""
        if self.is_recording: return False
        if not self._init_capture(): return False
        self.output_file_original = os.path.join(self.output_dir, self.output_filename)
        self.output_file_annotated = os.path.join(self.output_dir,
                                                  self.output_filename.replace(".mp4", "_annotated.mp4"))
        try:
            self.writer_original = cv2.VideoWriter(self.output_file_original, self.codec, self.fps, self.actual_res)
            if not self.writer_original.isOpened():
                raise IOError("Cannot open VideoWriter Original")

            if self.processor:
                self.writer_annotated = cv2.VideoWriter(self.output_file_annotated, self.codec, self.fps, self.actual_res)
                if not self.writer_annotated.isOpened():
                    raise IOError("Cannot open VideoWriter Annotated")

            if self.processor and hasattr(self.processor, 'reset'):
                self.processor.reset()

            self.is_recording = True
            self._stop.clear()
            self.thread = threading.Thread(target=self._loop, name=f"Rec-{self.webcam_id}", daemon=True)
            self.thread.start()
            log.info(f"Started recording cam {self.webcam_id} -> {self.output_file_original}")
            if self.processor:
                log.info(f"Started recording cam {self.webcam_id} -> {self.output_file_annotated}")
            return True
        except Exception as e:
            log.error(f"Cam {self.webcam_id} start failed: {e}")
            self._release()
            self.is_recording = False
            return False

    def _loop(self):
        """Recording loop: reads, processes, writes frames."""
        log.debug(f"Loop started for cam {self.webcam_id}")
        while not self._stop.is_set():
            if not self.capture or not self.capture.isOpened(): break
            ret, frame = self.capture.read()
            if not ret: time.sleep(0.05); continue
            try:
                if self.writer_original:
                    self.writer_original.write(frame)

                if self.processor and self.writer_annotated:
                    out_frame = self.processor.process(frame)
                    if out_frame.shape[1] != self.actual_res[0] or out_frame.shape[0] != self.actual_res[1]:
                        out_frame = cv2.resize(out_frame, self.actual_res)
                    self.writer_annotated.write(out_frame)

            except Exception as e:
                log.error(f"Cam {self.webcam_id} loop error: {e}", exc_info=False)
        log.debug(f"Loop ended for cam {self.webcam_id}")
        self._release()

    def stop_recording(self) -> Tuple:
        """Signals thread to stop and returns filename."""
        if not self.is_recording and not (self.thread and self.thread.is_alive()): return None
        log.info(f"Stopping cam {self.webcam_id}...")
        self._stop.set()
        if self.thread: self.thread.join(timeout=3.0)
        self.is_recording = False
        self._release()  # Ensure release called AFTER join attempt
        log.info(f"Stopped cam {self.webcam_id}. File: {self.output_file_original}")
        if self.processor:
            log.info(f"Stopped cam {self.webcam_id}. File: {self.output_file_annotated}")
        return self.output_file_original, self.output_file_annotated

    def _release(self):
        """Releases OpenCV capture and writer."""
        if self.capture:
            try:
                if self.capture.isOpened(): self.capture.release()
            except Exception:  # Catch potential errors during release
                pass  # Ignore release errors in simplified version
            finally:
                self.capture = None  # Ensure it's set to None

        if self.writer_original:
            try:
                if self.writer_original.isOpened():
                    self.writer_original.release()
            except Exception:
                pass
            finally:
                self.writer_original = None

        if self.writer_annotated:
            try:
                if self.writer_annotated.isOpened():
                    self.writer_annotated.release()
            except Exception:
                pass
            finally:
                self.writer_annotated = None
        log.debug(f"Resources released attempt for cam {self.webcam_id}")

    def get_processor(self) -> Optional[BaseProcessor]:
        return self.processor
