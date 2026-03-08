# AGENTS.md

This file provides guidance to AI coding agents when working with code in this repository.

## Project Overview

Synthetic Student Generator is a web application that generates calibration sets of rubric-aligned student work samples using LLM-driven personas. Teachers select a rubric template (or paste their own freeform rubric), enter an assignment prompt, choose proficiency levels, and receive a set of realistic student writing samples — one per proficiency level — with detailed metadata. The primary workflow is generating a calibration set for grading practice, not individual samples.

- **Backend:** FastAPI 0.115+ (Python 3.13) on Cloud Run
- **Frontend:** SvelteKit 2 + Vite SPA on Firebase Hosting
- **LLM:** Gemini 2.5 Flash via Google Gen AI SDK 1.x (structured JSON output)
- **Data:** No database -- rubric templates are bundled JSON; generated samples are ephemeral

**Status:** Pre-build (planning docs only, no code yet).

## Build & Run Commands

### Backend (`backend/` directory)
```bash
cd backend
pip install -r requirements.txt    # Install dependencies
uvicorn app.main:app --reload      # Local dev server on :8000
docker build -t ssg-backend .      # Build container
docker run -p 8080:8080 ssg-backend  # Run container locally
```

### Frontend (`frontend/` directory)
```bash
cd frontend
npm install                        # Install dependencies
npm run dev                        # SvelteKit dev server on :5173
npm run build                      # Production build to ./dist/ (static adapter)
npm run preview                    # Preview production build
```

### Deployment
```bash
bash scripts/deploy.sh all         # Deploy backend + frontend
bash scripts/deploy.sh backend     # Deploy backend to Cloud Run only
bash scripts/deploy.sh frontend    # Deploy frontend to Firebase Hosting only
```

## Architecture

### Request Flow
`Browser` -> `Firebase Hosting (SvelteKit SPA)` -> `Firebase Cloud Function (API Proxy)` -> `FastAPI (Cloud Run)` -> `Google Gen AI SDK` -> `Gemini 2.5 Flash` -> Structured JSON response -> `Frontend renders sample`

### Key Design Decisions
- **Calibration set as primary workflow:** Frontend sends parallel individual `POST /api/v1/generate` requests (one per proficiency level) and assembles results in a tabbed view. No batch endpoint needed.
- **Freeform rubric parsing:** Teachers can paste rubric text from any source (LMS, doc, etc.). Backend sends `rubric_text` to Gemini with a parsing prompt to extract structured dimensions before generation.
- **Structured output:** Uses Gemini's native `response_schema` parameter for constrained JSON decoding -- no regex parsing or retry loops for malformed output.
- **Persona system:** Parameterized persona templates (grade level, error patterns, voice traits) composed at request time rather than fixed profiles. Produces diverse, authentic student writing.
- **No database:** Rubric templates are static JSON bundled with the backend. Generated samples are returned to the client and not persisted.
- **Google Gen AI SDK:** Uses the `google-genai` package (replaces deprecated `vertexai.generative_models`). Unified interface for both Gemini API and Vertex AI.

### API Endpoints
- `POST /api/v1/generate` -- Generate a synthetic student work sample (rubric via template_id, rubric, or rubric_text + assignment + proficiency level)
- `GET /api/v1/templates` -- List available rubric templates
- `GET /api/v1/templates/{template_id}` -- Get a specific rubric template with level descriptors
- `GET /api/v1/health` -- Health check and service metadata

## Environment Setup

```bash
# TODO: Add environment setup once project is scaffolded
cp .env.example .env
# Required variables:
#   GCP_PROJECT_ID=your-gcp-project-id
#   GCP_REGION=us-central1 (default)
#   GEMINI_MODEL=gemini-2.5-flash (default)
```

Backend requires GCP credentials for Vertex AI Gemini. For local development, configure application default credentials or a service account key. In production, Cloud Run's service account (with "Vertex AI User" role) provides implicit auth.

## Project Documentation

Detailed specs live in `docs/`:
- [`docs/README.md`](docs/README.md) -- Documentation index and quick links
- [`docs/architecture.md`](docs/architecture.md) -- System architecture, tech stack, and design decisions
- [`docs/api-contracts.md`](docs/api-contracts.md) -- API endpoint specifications and Pydantic models
- [`docs/milestones.md`](docs/milestones.md) -- Development phases and deliverables
- [`docs/local-dev-guide.md`](docs/local-dev-guide.md) -- Local development setup
- [`docs/local-testing-guide.md`](docs/local-testing-guide.md) -- Testing guide (backend, API, frontend, manual)
- [`docs/production-deployment.md`](docs/production-deployment.md) -- GCP deployment guide
