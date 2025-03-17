#!/bin/bash

# Configuration
PROJECT_ID="next-25-roll-and-score"
REGION="us-central1"
SERVICE_NAME="roll-and-score"
IMAGE_NAME="vue-front-end-image"
REPOSITORY="roll-and-score-artifact-repo"

# Build the Docker image
echo "Building Docker image..."
docker build -t "$IMAGE_NAME" .

# Tag the Docker image
echo "Tagging Docker image..."
docker tag "$IMAGE_NAME" "$REGION"-docker.pkg.dev/"$PROJECT_ID"/"$REPOSITORY"/"$IMAGE_NAME"

# Authenticate Docker to GCP
echo "Authenticating Docker to GCP..."
gcloud auth configure-docker

# Push the Docker image
echo "Pushing Docker image..."
docker push "$REGION"-docker.pkg.dev/"$PROJECT_ID"/"$REPOSITORY"/"$IMAGE_NAME"

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
    --image "$REGION"-docker.pkg.dev/"$PROJECT_ID"/"$REPOSITORY"/"$IMAGE_NAME" \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --service-account="front-end-service-account@next-25-roll-and-score.iam.gserviceaccount.com"

echo "Deployment task is done!"

# Optionally, print the service URL
echo "Service URL:"
gcloud run services describe "$SERVICE_NAME" --platform managed --region="$REGION" --format='value(status.url)'
