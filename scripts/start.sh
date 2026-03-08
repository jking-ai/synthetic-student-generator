#!/usr/bin/env bash
# Start the backend dev server with Vertex AI credentials.
# Usage: bash scripts/start.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_DIR/backend"

# Source .env if it exists
if [[ -f "$BACKEND_DIR/.env" ]]; then
    set -a
    source "$BACKEND_DIR/.env"
    set +a
    echo "✓ Loaded .env from backend/"
fi

# Check for GCP credentials
if [[ -n "${GOOGLE_APPLICATION_CREDENTIALS:-}" && -f "$GOOGLE_APPLICATION_CREDENTIALS" ]]; then
    echo "✓ GCP credentials found: $GOOGLE_APPLICATION_CREDENTIALS"
    echo "  Vertex AI access enabled"
else
    echo "⚠ No GCP credentials found."
    echo "  Copy backend/.env.example to backend/.env and set GOOGLE_APPLICATION_CREDENTIALS"
    echo "  The API will start but Gemini calls will fail."
fi

echo ""
echo "Starting backend on http://localhost:8000 ..."
echo ""

cd "$BACKEND_DIR"

# Install deps if needed
if [[ ! -d ".venv" ]] && ! python3 -c "import fastapi" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -q -r requirements.txt
fi

exec uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
