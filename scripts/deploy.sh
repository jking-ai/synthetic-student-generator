#!/usr/bin/env bash
# Deploy the Synthetic Student Generator to GCP.
#   - Backend → Cloud Run (Docker image)
#   - Frontend → Firebase Hosting (static SPA + API proxy function)
#
# Prerequisites:
#   - gcloud CLI authenticated with your GCP project
#   - firebase CLI authenticated
#   - Environment variables set (or update defaults below)
#   - Service account with Vertex AI User role
#
# Environment variables (override defaults):
#   GCP_PROJECT       - Your GCP project ID
#   GCP_REGION        - GCP region (default: us-central1)
#   SERVICE_NAME      - Cloud Run service name (default: synthetic-student-generator)
#   SERVICE_ACCOUNT   - Service account email for Cloud Run
#
# Usage: bash scripts/deploy.sh [backend|frontend|all]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

GCP_PROJECT="${GCP_PROJECT:-$(gcloud config get-value project 2>/dev/null)}"
GCP_REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-synthetic-student-generator}"
SERVICE_ACCOUNT="${SERVICE_ACCOUNT:-${SERVICE_NAME}-sa@${GCP_PROJECT}.iam.gserviceaccount.com}"

if [[ -z "$GCP_PROJECT" || "$GCP_PROJECT" == "(unset)" ]]; then
    echo "Error: GCP_PROJECT not set. Either export GCP_PROJECT or run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "Project: $GCP_PROJECT | Region: $GCP_REGION | Service: $SERVICE_NAME"
echo ""

TARGET="${1:-all}"

deploy_backend() {
    echo "═══════════════════════════════════════"
    echo "  Deploying Backend → Cloud Run"
    echo "═══════════════════════════════════════"
    echo ""

    cd "$BACKEND_DIR"

    # Deploy from source (uses Dockerfile)
    gcloud run deploy "$SERVICE_NAME" \
        --source . \
        --region "$GCP_REGION" \
        --project "$GCP_PROJECT" \
        --service-account "$SERVICE_ACCOUNT" \
        --allow-unauthenticated \
        --set-env-vars="GCP_PROJECT_ID=${GCP_PROJECT},GCP_REGION=${GCP_REGION},GEMINI_MODEL=gemini-2.5-flash" \
        --memory 512Mi \
        --cpu 1 \
        --min-instances 0 \
        --max-instances 2 \
        --timeout 300

    # Get the deployed URL
    BACKEND_URL=$(gcloud run services describe "$SERVICE_NAME" \
        --region "$GCP_REGION" \
        --project "$GCP_PROJECT" \
        --format="value(status.url)")

    echo ""
    echo "✓ Backend deployed: $BACKEND_URL"
    echo "  Health check: $BACKEND_URL/api/v1/health"
    echo ""

    # Verify health
    echo "Verifying health endpoint..."
    if curl -sf "$BACKEND_URL/api/v1/health" | python3 -m json.tool; then
        echo ""
        echo "✓ Backend is healthy"
    else
        echo ""
        echo "⚠ Health check failed — the service may still be warming up"
    fi
}

deploy_frontend() {
    echo "═══════════════════════════════════════"
    echo "  Deploying Frontend → Firebase Hosting"
    echo "═══════════════════════════════════════"
    echo ""

    # Get backend URL for the API proxy
    BACKEND_URL=$(gcloud run services describe "$SERVICE_NAME" \
        --region "$GCP_REGION" \
        --project "$GCP_PROJECT" \
        --format="value(status.url)" 2>/dev/null || echo "")

    if [[ -z "$BACKEND_URL" ]]; then
        echo "⚠ Backend not deployed yet. Deploy backend first: bash scripts/deploy.sh backend"
        exit 1
    fi

    echo "Backend URL: $BACKEND_URL"
    echo ""

    cd "$FRONTEND_DIR"

    # Build the SvelteKit static site
    echo "Building frontend..."
    npm run build

    # Install function deps
    echo "Installing function dependencies..."
    cd functions
    npm install
    npm run build
    cd ..

    # Set the API_TARGET parameter for the Cloud Function
    echo "Setting API_TARGET parameter..."
    firebase functions:config:set api.target="$BACKEND_URL" --project "$GCP_PROJECT" 2>/dev/null || true

    # Ensure Firebase hosting target is configured
    firebase target:apply hosting synthetic-student-generator "${FIREBASE_HOSTING_SITE:-synthetic-student-gen}" --project "$GCP_PROJECT" 2>/dev/null || true

    # Deploy hosting + functions
    echo "Deploying to Firebase..."
    firebase deploy --project "$GCP_PROJECT"

    echo ""
    echo "✓ Frontend deployed"
    echo ""
}

case "$TARGET" in
    backend)
        deploy_backend
        ;;
    frontend)
        deploy_frontend
        ;;
    all)
        deploy_backend
        echo ""
        deploy_frontend
        ;;
    *)
        echo "Usage: bash scripts/deploy.sh [backend|frontend|all]"
        exit 1
        ;;
esac

echo "═══════════════════════════════════════"
echo "  Deployment complete!"
echo "═══════════════════════════════════════"
