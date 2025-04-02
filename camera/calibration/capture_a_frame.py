import argparse
import os  # For checking file existence
import time

import cv2


def capture_a_frame(source=0, skip_frame=10):
    """Captures a single photo from the provided webcam index or video path."""
    try:
        # Open the video source (webcam or video file)
        cap = cv2.VideoCapture(source)

        # Check if the video source is opened successfully
        if not cap.isOpened():
            if isinstance(source, str):  # Check if source is a string (file path)
                print(f"Error: Could not open video file: {source}")
            else:
                print(f"Error: Could not open webcam (index: {source})")
            return

        # Give the source a moment to initialize (especially for webcams)
        time.sleep(1)

        ret, frame = cap.read()
        frame_count = 0

        while frame_count < skip_frame:
            ret, frame = cap.read()  # Read a frame from the video source
            frame_count += 1

            # Check if a frame was successfully read
            if not ret:
                print("Error: Could not read frame.")
                return

        # Save the captured frame as an image
        filename = "captured_frame.jpg"  # Generic filename
        cv2.imwrite(filename, frame)
        print(f"Photo saved as {filename}")

        # Release the video source
        cap.release()

    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Capture a frame from a webcam or video file."
    )
    parser.add_argument(
        "source",
        help="Webcam index (integer) or path to a video file (string).",
    )

    args = parser.parse_args()

    # Determine if the source is a number (webcam index) or a string (file path)
    try:
        source_value = int(args.source)
    except ValueError:
        source_value = args.source  # Keep it as a string (file path)
        if not os.path.exists(source_value):
            print(f"Error: Video file not found: {source_value}")
            return

    capture_a_frame(source_value)


if __name__ == "__main__":
    main()
