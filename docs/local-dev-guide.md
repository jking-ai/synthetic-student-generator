# Local Development Guide

How to set up, run, and develop Synthetic Student Generator on your local machine.

---

## Prerequisites

| Tool | Version | Check |
|------|---------|-------|
| Python | 3.13+ | `python --version` |
| Node.js | 20+ | `node --version` |
| Docker | 24+ | `docker --version` |
| Firebase CLI | 13+ | `firebase --version` |
| Google Cloud SDK | latest | `gcloud --version` |

---

## 1. Environment Setup

<!-- TODO: Add detailed environment setup steps once the project is scaffolded -->

```bash
# Clone the repository
git clone <repo-url>
cd synthetic-student-generator

# Copy environment template
cp .env.example .env
# Fill in: GCP_PROJECT_ID, GCP_REGION, GEMINI_MODEL
```

### GCP Credentials

<!-- TODO: Document credential setup for local Vertex AI access -->
<!-- Options: application default credentials or service account key -->

---

## 2. Start the Backend

<!-- TODO: Add backend startup instructions once FastAPI app is created -->

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Verify Backend

```bash
curl http://localhost:8000/api/v1/health
```

---

## 3. Start the Frontend

<!-- TODO: Add frontend startup instructions once React app is scaffolded -->

```bash
cd frontend
npm install
npm run dev
# Vite dev server starts on http://localhost:5173
```

---

## 4. Quick Verification

<!-- TODO: Add end-to-end verification steps -->

1. Backend health check returns 200
2. Frontend loads in browser at `http://localhost:5173`
3. Submitting a generate request returns a student sample

---

## Troubleshooting

<!-- TODO: Add common issues and solutions -->

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Ensure virtual environment is activated and dependencies are installed |
| CORS errors in browser | Verify backend CORS config includes `http://localhost:5173` |
| Gemini authentication failure | Check GCP credentials are configured correctly |
| Port already in use | Kill the existing process or use a different port |
