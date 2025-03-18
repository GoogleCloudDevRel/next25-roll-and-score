#!/bin/bash

# Prompt the user for the environment (dev/prod)
while true; do
    read -p "Run in (dev/prod)? " environment
    case "$environment" in
        [Dd][Ee][Vv]) environment="dev"; break ;;
        [Pp][Rr][Oo][Dd]) environment="prod"; break ;;
        *) echo "Invalid input. Please enter 'dev' or 'prod'." ;;
    esac
done

echo "Starting deployment task to ${environment}..."

set -e

# Copy actual values to config file
firebase_config="/src/config/firebaseConfig.js"
prod_firebase_config="/src/config/firebaseConfigProd.js"

cp "$prod_firebase_config" "$firebase_config"

# Configuration
PROJECT_ID="next-25-roll-and-score"
REGION="us-central1"
SERVICE_NAME="${environment}-roll-and-score"
IMAGE_NAME="${environment}-vue-front-end-image"
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
    --region "$REGION" \
    --service-account="front-end-service-account@next-25-roll-and-score.iam.gserviceaccount.com" \
    --platform managed \
    --allow-unauthenticated

echo "Deployment task is finished!"

# Restore firebaseConfig.js file
git restore "$firebase_config"
