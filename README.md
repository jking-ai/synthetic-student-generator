# Synthetic Student Generator

**One-line summary:** Generate realistic student writing samples for grading calibration — in seconds, not hours. A web application that produces calibration sets of rubric-aligned student work across proficiency levels using LLM-driven personas.

---

## Problem Statement

Teachers need to calibrate their grading against rubrics, but obtaining a diverse set of student work samples at varying proficiency levels is difficult and time-consuming. Real student work raises privacy concerns, and manually writing exemplars is tedious and often lacks the authentic variation found in actual student submissions. Teachers need on-demand access to realistic student writing samples that span the full range of a rubric -- from below-expectations to exemplary -- so they can practice scoring consistently before grading real work.

## Target User Persona

**Name:** Ms. Carter, 8th-grade English Language Arts teacher

- Has 6 years of teaching experience
- Leads her department's grading calibration sessions each quarter
- Currently spends 3-4 hours hand-writing sample essays at different rubric levels for calibration exercises
- Wants samples that feel authentically student-written (age-appropriate vocabulary, common mistakes, varied voice)
- Needs samples mapped to specific rubric dimensions (e.g., "Proficient in organization, Developing in evidence use")

## Skills and Engineering Patterns Showcased

| Pattern | Description |
|---------|-------------|
| **Structured Output (JSON mode)** | Enforcing deterministic JSON schema from Gemini responses for consistent downstream parsing |
| **Complex System Instructions** | Crafting multi-layered system prompts that maintain distinct student personas with age-appropriate voice, skill profiles, and error patterns |
| **Persona Engineering** | Designing a persona specification schema that controls writing level, vocabulary, common mistakes, and rubric-dimension performance independently |
| **FastAPI Backend Design** | Clean REST API with Pydantic models, proper error handling, and CORS configuration for frontend consumption |
| **Cloud Run Deployment** | Containerized Python service deployed to Google Cloud Run with environment-based configuration |
| **React Frontend** | Lightweight single-page application with form-driven UX for rubric input and sample display |
| **Vertex AI Integration** | Using the Google Gen AI SDK to call Gemini models from a Cloud Run service with proper authentication |

## Success Criteria

1. **Calibration Set Workflow:** A teacher can select a rubric (template or freeform paste), enter an assignment prompt, choose proficiency levels, and receive a calibration set of student work samples (one per level) within ~15 seconds.
2. **Freeform Rubric Parsing:** A teacher can paste a rubric from their LMS or any document, and the system parses it into structured dimensions without manual formatting.
3. **Quality Differentiation:** Generated samples are distinguishable by proficiency level -- a reader should be able to rank four samples (Below, Approaching, Proficient, Exemplary) in the correct order at least 80% of the time. All 4 templates produce distinguishable quality across levels.
4. **Persona Consistency:** Samples generated with the same persona specification exhibit consistent voice and error patterns across multiple generations.
5. **Structured Output:** Every LLM response conforms to the defined JSON schema with zero parsing failures in the happy path.
6. **Deployable:** The backend runs on Cloud Run and the frontend is hosted on Firebase Hosting, both accessible via public URLs.
7. **Portfolio-Ready:** The project README, architecture docs, and live demo clearly communicate the engineering decisions to a technical reviewer.

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/architecture.md) | System design, tech stack, data flow, and design decisions |
| [API Contracts](docs/api-contracts.md) | Endpoint specs, request/response examples, Pydantic models |
| [Milestones](docs/milestones.md) | Development phases and deliverables |
| [Local Development Guide](docs/local-dev-guide.md) | Prerequisites, environment setup, running locally |
| [Local Testing Guide](docs/local-testing-guide.md) | Backend tests, API testing, manual testing |
| [Production Deployment](docs/production-deployment.md) | GCP deployment, Docker, Cloud Run, Firebase Hosting |

## Level of Effort

**Low** -- Estimated 2-3 focused implementation sessions.

- Backend: ~4 hours (FastAPI setup, prompt engineering, Gemini integration, structured output)
- Frontend: ~3 hours (React app with form, results display, template selector)
- Deployment: ~2 hours (Dockerfile, Cloud Run deploy, Firebase Hosting)
- Polish: ~2 hours (error handling, loading states, rubric templates)
