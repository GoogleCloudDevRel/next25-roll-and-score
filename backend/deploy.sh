#!/bin/bash

set -e 

# Environment variables
PROJECT_ID="next-25-roll-and-score"
REGION="us-central1"
REPOSITORY="roll-and-score-artifact-repo"
SERVICE_NAME="roll-and-score-backend"

# Build the Docker image
echo "Building Docker image..."
docker build -t "$SERVICE_NAME" .

# Tag the Docker image
echo "Tagging Docker image..."
docker tag "$SERVICE_NAME" "$REGION"-docker.pkg.dev/"$PROJECT_ID"/"$REPOSITORY"/"$SERVICE_NAME"

# Authenticate Docker to GCP
echo "Authenticating Docker to GCP..."
gcloud auth configure-docker

# Push the Docker image
echo "Pushing Docker image..."
docker push "$REGION"-docker.pkg.dev/"$PROJECT_ID"/"$REPOSITORY"/"$SERVICE_NAME"

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
    --image "$REGION"-docker.pkg.dev/"$PROJECT_ID"/"$REPOSITORY"/"$SERVICE_NAME" \
    --region "$REGION" \
    --service-account="back-end-service-account" \
    --platform managed \
    --cpu 2 \
    --memory 4Gi \
    --allow-unauthenticated

echo "Deployment task is finished!"
