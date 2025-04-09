### Step 1: Get a frame from either a webcam feed or a video

- Capturing from a webcam feed
    ```commandline
    python capture_a_frame.py 0
    ```

- Capturing from a video
    ```commandline
    python capture_a_frame.py video_file_path
    ```

### Step 2: Annotate bounding boxes to the captured frame

- Go to [VGG Annotator](https://robots.ox.ac.uk/~vgg/software/via/via_demo.html)
- Import the captured frame (remove other preloaded images)
- Draw bounding boxes for the score holes using the tool
- Label the bounding boxes according to score
- Save the project and it will download a json file automatically

### Step 3: Extract bounding boxes and draw it on the captured frame

```commandline
python extract_bbox_info.py via_project.json
```