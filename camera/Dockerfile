FROM python:3.11-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY services services
COPY utils utils
COPY config.py .
COPY main_controller.py .

COPY scoring_cam1_2.avi .
COPY scoring_cam2_2.avi .

CMD ["python", "main_controller.py"]
