# Milestones -- Synthetic Student Generator

## Phase 1: Foundation

**Goal:** Establish the project skeleton, confirm Gemini integration works end-to-end, and verify structured output.

**Estimated effort:** 1 session (~3 hours)

### Deliverables

#### 1.1 Backend Project Setup

**Acceptance criteria:**
- Python 3.13 project initialized with `requirements.txt` containing: `fastapi[standard]>=0.115`, `google-genai>=1.0`, `pydantic>=2.0`, `pydantic-settings>=2.0`, `uvicorn>=0.34`
- `Dockerfile` builds and runs locally with `docker build -t ssg-backend . && docker run -p 8000:8000 ssg-backend`
- `app/main.py` creates a FastAPI app instance with CORS middleware configured for `localhost:5173` and a placeholder production origin
- `app/config.py` loads settings from environment variables: `GCP_PROJECT_ID`, `GCP_REGION` (default: `us-central1`), `GEMINI_MODEL` (default: `gemini-2.5-flash`)
- `GET /api/v1/health` returns the health response JSON as defined in api-contracts.md
- Running `uvicorn app.main:app --reload` starts the server without errors

#### 1.2 Gemini Client Integration

**Acceptance criteria:**
- `app/services/gemini_client.py` initializes the `google-genai` client configured for Vertex AI (`vertexai=True`, project and location from config)
- A standalone test script (`scripts/test_gemini.py`) sends a simple prompt to Gemini 2.5 Flash and prints the response, confirming authentication works
- The client supports passing `response_mime_type="application/json"` and a `response_schema` dict to enforce structured output
- Error handling wraps SDK exceptions and raises a custom `GenerationError` with the original error message

#### 1.3 Structured Output Proof of Concept

**Acceptance criteria:**
- `app/models/schemas.py` defines the Gemini response schema as a Python dict matching the `GeneratedSample` structure (student_response, proficiency_scores, persona_notes, writing_traits)
- A test script (`scripts/test_structured_output.py`) calls Gemini with the response schema and a hardcoded rubric/prompt, and successfully parses the JSON response into the Pydantic `GeneratedSample` model
- The parsed response contains all required fields with correct types
- Test is run 3 times to confirm consistency (zero parse failures)

**Dependencies:** 1.2 must be complete before 1.3.

---

## Phase 2: Core Features — Calibration Set Workflow

**Goal:** Implement the full generate endpoint with freeform rubric parsing, 4 rubric templates, and a 4-screen frontend that generates calibration sets (one sample per proficiency level, in parallel).

**Estimated effort:** 2 sessions (~5 hours)

### Deliverables

#### 2.1 Prompt Builder and Persona System

**Acceptance criteria:**
- `app/prompts/persona_template.txt` contains a system instruction template with placeholders: `{grade_level}`, `{proficiency_level}`, `{rubric_dimensions}`, `{error_patterns}`, `{voice_traits}`
- `app/services/prompt_builder.py` exposes a `build_system_instruction(request: GenerateRequest, rubric_detail: dict) -> str` function that populates the template
- The system instruction clearly directs the model to: (a) role-play as a student at the specified grade level, (b) write at the target proficiency level, (c) incorporate specified error patterns naturally, (d) match the voice traits described
- A separate `build_user_prompt(assignment_prompt: str) -> str` function wraps the assignment with framing (e.g., "You are a student in class. Your teacher gave you this assignment: ...")
- Unit test: given a known input, the assembled system instruction contains all expected rubric dimension names and the correct proficiency level string

#### 2.2 Freeform Rubric Parsing

**Acceptance criteria:**
- `app/services/rubric_parser.py` exposes a `parse_rubric_text(rubric_text: str) -> CustomRubric` function
- Sends `rubric_text` to Gemini with a parsing prompt and `response_schema` enforcing `CustomRubric` structure
- Successfully parses common rubric formats: numbered scales (1-4), named levels (Below/Approaching/Proficient/Exemplary), table-style, and narrative descriptions
- Returns a valid `CustomRubric` with dimension names and level descriptors extracted from the freeform text
- On parse failure, raises a descriptive error (not a generic 500)

#### 2.3 Generate Endpoint

**Acceptance criteria:**
- `POST /api/v1/generate` accepts the request body as defined in api-contracts.md (including new `rubric_text` field)
- Request validation: returns 400 if none of `template_id`, `rubric`, or `rubric_text` is provided
- Rubric resolution priority: `template_id` > `rubric` > `rubric_text`
- If `rubric_text` is provided (and no `template_id` or `rubric`), calls `rubric_parser.parse_rubric_text()` before generation
- If `template_id` is provided, the rubric is loaded from `app/data/rubric_templates.json`
- If `template_id` is not found, returns 404 with `INVALID_TEMPLATE_ID` error code
- Calls `prompt_builder` to assemble instructions, then `gemini_client` to generate, then parses the response
- Returns the full `GenerateResponse` JSON with `sample` and `metadata` fields
- `metadata.generation_time_ms` accurately reflects the Gemini API call duration
- `metadata.request_id` is a unique UUID prefixed with `req_`
- On Gemini failure, returns 500 with `GENERATION_FAILED` error code and descriptive message

#### 2.4 Rubric Templates (4 templates)

**Acceptance criteria:**
- `app/data/rubric_templates.json` contains 4 templates:
  1. `6-trait-writing` — 6-Trait Writing Rubric (grades 6-12)
  2. `argumentative-persuasive` — Argumentative/Persuasive Essay (grades 6-10)
  3. `narrative-elementary` — Narrative Writing (grades 3-5)
  4. `informational-explanatory` — Informational/Explanatory Writing (grades 6-10)
- Each template includes: `id`, `name`, `description`, `grade_range`, and `dimensions` array with `name` and `levels` (Exemplary/Proficient/Approaching/Below descriptors)
- `GET /api/v1/templates` returns the template list (summary: id, name, description, grade_range, dimension names only)
- `GET /api/v1/templates/{template_id}` returns the full template with level descriptors
- Templates match the JSON structures documented in api-contracts.md

#### 2.5 Frontend — Screen 1: Landing Page

**Acceptance criteria:**
- React 19 project initialized with Vite 7: `npm create vite@latest frontend -- --template react`
- `src/api/client.js` exports an `apiClient` object with methods: `health()`, `getTemplates()`, `getTemplate(id)`, `generate(requestBody)`
- API base URL is configurable via `VITE_API_URL` environment variable (defaults to `http://localhost:8000`)
- Landing page displays: title + tagline ("Generate realistic student writing samples for grading calibration — in seconds, not hours."), a 3-step visual (Choose a rubric → Enter your prompt → Get student samples), one hardcoded example showing output quality (no live API call), and a CTA button ("Create Calibration Set") that navigates to the Configure screen

#### 2.6 Frontend — Screen 2: Configure Generation

**Acceptance criteria:**
- Single-page form with three sections:
  - **Section A — Rubric Selection:** Toggle between "Use a Template" (default, 4 selectable template cards in a grid with collapsible rubric preview) and "Paste Your Own" (large textarea for freeform rubric text)
  - **Section B — Assignment Details:** Assignment prompt textarea (required), grade level dropdown (default: 8, range: 3-12), proficiency level checkboxes (Below | Approaching | Proficient | Exemplary, all checked by default, min 1)
  - **Section C — Generate Button:** "Generate [N] Samples" where N updates dynamically based on checked proficiency levels
- Form submission sends parallel individual `POST /api/v1/generate` requests (one per checked proficiency level) and transitions to the Loading screen

#### 2.7 Frontend — Screen 3: Loading State

**Acceptance criteria:**
- Displays per-level progress cards (one per requested proficiency level)
- Each card shows a spinner while its request is in flight, transitions to a checkmark on completion
- Auto-transitions to the Results screen when all requests complete
- On individual request failure, the card shows an error state with a retry option

#### 2.8 Frontend — Screen 4: Results View

**Acceptance criteria:**
- Tabbed view with one tab per proficiency level (color-coded: red for Below, orange for Approaching, green for Proficient, blue for Exemplary)
- Active tab shows: proficiency badge header with word count and tone, full student response in readable format, collapsible footer with rubric dimension scores, persona notes, and writing traits
- Actions: Copy (per sample), Copy All (formatted with level headers), Start Over (returns to Configure screen), Edit & Regenerate (returns to Configure screen with form pre-filled)

**Dependencies:** 2.5 → 2.6 → 2.7 → 2.8. Backend endpoints (2.1-2.4) must be complete before 2.6 (frontend needs a working API).

---

## Phase 3: Polish and Demo

**Goal:** Deploy to GCP, refine the UI, validate calibration set quality, and ensure the project is portfolio-ready.

**Estimated effort:** 1 session (~3 hours)

### Deliverables

#### 3.1 Cloud Run Deployment

**Acceptance criteria:**
- `Dockerfile` uses a multi-stage build: Python 3.13-slim base, copies requirements and installs deps, copies app code, runs with `uvicorn`
- The container exposes port 8080 (Cloud Run default)
- `gcloud run deploy synthetic-student-generator --source . --region us-central1 --allow-unauthenticated` succeeds
- The Cloud Run service has the `GCP_PROJECT_ID` and `GCP_REGION` environment variables set
- The Cloud Run service account has the `Vertex AI User` IAM role
- `GET /api/v1/health` returns 200 from the deployed URL

#### 3.2 Firebase Hosting Deployment

**Acceptance criteria:**
- `frontend/firebase.json` configures Firebase Hosting to serve `dist/` with SPA rewrite rules
- `npm run build` produces a production build in `dist/`
- `VITE_API_URL` is set to the Cloud Run production URL during the build
- `firebase deploy --only hosting` succeeds and the app is accessible at the Firebase Hosting URL
- CORS on the backend is updated to include the Firebase Hosting domain

#### 3.3 UI Polish

**Acceptance criteria:**
- Responsive layout works on desktop (1200px+) and tablet (768px+); mobile is not required but should not break
- Landing page example is visually compelling and demonstrates output quality
- Loading state progress cards are smooth and informative
- Tabbed results view has clear color-coding and readable typography
- Error states display a clear message and a "Try Again" button
- Page title and meta description are set for the portfolio showcase

#### 3.4 Calibration Set Quality Validation

**Acceptance criteria:**
- Generate a full calibration set (all 4 proficiency levels) for each of the 4 templates with the same assignment prompt
- Manually verify that: (a) Below samples contain noticeably more errors and weaker structure than Proficient samples, (b) Exemplary samples demonstrate sophisticated vocabulary, varied sentence structure, and strong organization, (c) samples at the same level have distinct voices (not copy-paste variations), (d) all 4 templates produce distinguishable quality differences across proficiency levels
- Test freeform rubric parsing with a rubric pasted from a real LMS or teacher document
- Verify parallel request orchestration completes within ~15 seconds for 4 samples
- Adjust the persona template system instruction if quality does not meet criteria

#### 3.5 Project Documentation

**Acceptance criteria:**
- `README.md` at the project root is updated with: live demo links (Cloud Run API + Firebase frontend), screenshots or sample output, setup instructions for local development, and a "Technical Highlights" section calling out structured output, persona engineering, freeform rubric parsing, and calibration set generation
- All four planning docs (README.md, architecture.md, api-contracts.md, milestones.md) remain accurate and reflect the final implementation
- Code includes docstrings on all public functions and classes

**Dependencies:** 3.1 and 3.2 must be complete before 3.3 (need deployed endpoints for final polish). 3.4 can run in parallel with 3.1/3.2 using local endpoints.
