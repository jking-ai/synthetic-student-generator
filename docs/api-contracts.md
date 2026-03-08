# API Contracts -- Synthetic Student Generator

## Base URL

- **Local development:** `http://localhost:8000`
- **Production:** `https://synthetic-student-generator-<hash>-uc.a.run.app`

All endpoints are prefixed with `/api/v1`.

---

## Endpoints Overview

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/health` | Health check and service metadata |
| `GET` | `/api/v1/templates` | List available rubric templates |
| `GET` | `/api/v1/templates/{template_id}` | Get a specific rubric template by ID |
| `POST` | `/api/v1/generate` | Generate a synthetic student work sample |

---

## Error Response Format

All error responses follow a consistent format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable description of what went wrong.",
    "details": []
  }
}
```

### Error Codes

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 400 | `VALIDATION_ERROR` | Request body failed Pydantic validation |
| 400 | `INVALID_TEMPLATE_ID` | The specified template_id does not exist |
| 422 | `UNPROCESSABLE_ENTITY` | FastAPI automatic validation error |
| 500 | `GENERATION_FAILED` | The LLM call failed or returned an unparseable response |
| 500 | `INTERNAL_ERROR` | Unexpected server error |
| 503 | `MODEL_UNAVAILABLE` | The Gemini model is temporarily unavailable |

---

## Endpoint Details

### GET /api/v1/health

Returns service status and metadata. Used by Cloud Run health checks and frontend connectivity verification.

**Request:** No parameters.

**Response (200 OK):**

```json
{
  "status": "healthy",
  "service": "synthetic-student-generator",
  "version": "1.0.0",
  "model": "gemini-2.5-flash"
}
```

---

### GET /api/v1/templates

Returns a list of all available rubric templates. Templates are bundled with the backend as static data.

**Request:** No parameters.

**Response (200 OK):**

```json
{
  "templates": [
    {
      "id": "6-trait-writing",
      "name": "6-Trait Writing Rubric",
      "description": "Standard 6-trait analytical writing rubric covering Ideas, Organization, Voice, Word Choice, Sentence Fluency, and Conventions.",
      "grade_range": "6-12",
      "dimensions": [
        "Ideas",
        "Organization",
        "Voice",
        "Word Choice",
        "Sentence Fluency",
        "Conventions"
      ]
    },
    {
      "id": "argumentative-persuasive",
      "name": "Argumentative/Persuasive Essay",
      "description": "Rubric for argumentative and persuasive essay writing, emphasizing claims, evidence, and counterarguments.",
      "grade_range": "6-10",
      "dimensions": [
        "Claim/Thesis",
        "Evidence and Reasoning",
        "Counterargument",
        "Organization",
        "Conventions"
      ]
    },
    {
      "id": "narrative-elementary",
      "name": "Narrative Writing (Elementary)",
      "description": "Elementary-level narrative writing rubric for grades 3-5.",
      "grade_range": "3-5",
      "dimensions": [
        "Story Structure",
        "Character Development",
        "Descriptive Language",
        "Spelling and Grammar"
      ]
    },
    {
      "id": "informational-explanatory",
      "name": "Informational/Explanatory Writing",
      "description": "Rubric for informational and explanatory writing, focusing on topic development, text structure, and academic language.",
      "grade_range": "6-10",
      "dimensions": [
        "Topic Development",
        "Text Structure",
        "Academic Language",
        "Use of Sources",
        "Conventions"
      ]
    }
  ]
}
```

---

### GET /api/v1/templates/{template_id}

Returns a single rubric template with full rubric detail including level descriptors for each dimension.

**Request:** Path parameter `template_id` (string).

**Response (200 OK):**

```json
{
  "id": "6-trait-writing",
  "name": "6-Trait Writing Rubric",
  "description": "Standard 6-trait analytical writing rubric covering Ideas, Organization, Voice, Word Choice, Sentence Fluency, and Conventions.",
  "grade_range": "6-12",
  "dimensions": [
    {
      "name": "Ideas",
      "levels": {
        "Exemplary": "The writing is clear, focused, and well-developed with rich, relevant details and examples that engage the reader.",
        "Proficient": "The writing is focused with adequate development. Supporting details are relevant but may be general.",
        "Approaching": "The topic is apparent but development is limited or general. Details are sparse or tangential.",
        "Below": "The writing lacks a central idea. Development is minimal or absent."
      }
    },
    {
      "name": "Organization",
      "levels": {
        "Exemplary": "Structure enhances the central idea. Transitions are smooth and connect ideas logically.",
        "Proficient": "Organization is clear with a recognizable structure. Transitions are present and functional.",
        "Approaching": "Attempts at organization are present but inconsistent. Transitions are weak or formulaic.",
        "Below": "No clear organizational structure. Ideas appear random or disconnected."
      }
    }
  ]
}
```

**Response (404 Not Found):**

```json
{
  "error": {
    "code": "INVALID_TEMPLATE_ID",
    "message": "No template found with ID 'nonexistent-id'.",
    "details": []
  }
}
```

---

### POST /api/v1/generate

Generate a synthetic student work sample based on a rubric, assignment prompt, and target proficiency level.

**Request Headers:**
- `Content-Type: application/json`

**Request Body Schema:**

```json
{
  "assignment_prompt": "string (required) -- The writing prompt the student should respond to.",
  "proficiency_level": "string (required) -- One of: Below, Approaching, Proficient, Exemplary.",
  "rubric": "object (optional) -- Custom rubric definition with structured dimensions.",
  "rubric_text": "string (optional) -- Freeform rubric text (e.g., pasted from an LMS). Backend parses it into structured format via Gemini.",
  "template_id": "string (optional) -- ID of a bundled rubric template. If provided, rubric and rubric_text are ignored.",
  "grade_level": "integer (optional, default: 8) -- Target student grade level (3-12).",
  "persona_config": "object (optional) -- Fine-grained persona controls."
}
```

> **Rubric resolution priority:** `template_id` > `rubric` > `rubric_text`. At least one must be provided.

**Concrete Request Example -- Using a template:**

```json
{
  "assignment_prompt": "Write a persuasive essay arguing whether schools should adopt a four-day school week. Use at least two pieces of evidence to support your position.",
  "proficiency_level": "Proficient",
  "template_id": "6-trait-writing",
  "grade_level": 8
}
```

**Concrete Request Example -- Using a custom rubric:**

```json
{
  "assignment_prompt": "Describe a time when you faced a challenge and explain how you overcame it.",
  "proficiency_level": "Approaching",
  "rubric": {
    "name": "Personal Narrative Rubric",
    "dimensions": [
      {
        "name": "Narrative Arc",
        "levels": {
          "Exemplary": "Clear beginning, rising action, climax, and resolution with purposeful pacing.",
          "Proficient": "Contains all narrative elements with adequate pacing.",
          "Approaching": "Some narrative elements present but pacing is uneven or elements are missing.",
          "Below": "No discernible narrative structure."
        }
      },
      {
        "name": "Descriptive Detail",
        "levels": {
          "Exemplary": "Vivid sensory details create a strong sense of place and emotion.",
          "Proficient": "Adequate detail supports the narrative.",
          "Approaching": "Details are sparse or generic.",
          "Below": "Little to no descriptive detail."
        }
      }
    ]
  },
  "grade_level": 6,
  "persona_config": {
    "error_patterns": ["run-on sentences", "informal tone shifts"],
    "voice_traits": ["enthusiastic", "conversational"]
  }
}
```

**Concrete Request Example -- Using freeform rubric text:**

```json
{
  "assignment_prompt": "Write an informational essay explaining the water cycle. Include at least three stages and use transition words.",
  "proficiency_level": "Approaching",
  "rubric_text": "4 - Exceeds: Thorough explanation with scientific vocabulary, clear transitions, and accurate details.\n3 - Meets: Adequate explanation covering main stages with some transitions.\n2 - Approaching: Incomplete explanation, missing stages or weak transitions.\n1 - Below: Minimal or inaccurate explanation with no clear structure.",
  "grade_level": 7
}
```

> The backend sends `rubric_text` to Gemini with a parsing prompt that extracts dimension names, level labels, and descriptors into the `CustomRubric` structure before proceeding with sample generation.

**Response (200 OK):**

```json
{
  "sample": {
    "student_response": "I think schools should definately switch to a four-day school week because it would help students and teachers both. First of all, students would have more time to rest and do activities outside of school. According to an article I read, schools in Colorado that tried four-day weeks saw their attendance go up by 15%. Thats a big deal because when students actually come to school they learn more.\n\nSecond, teachers would have an extra day to plan their lessons and grade papers. My mom is a teacher and she always says she never has enough time to get everything done. If she had Fridays off she could plan better lessons for us during the week.\n\nSome people might say that students would fall behind with less school days, but I disagree. The schools that switched made their other four days a little longer, so students still got the same amount of learning time. Plus students were more focused because they werent as tired.\n\nIn conclusion, I believe the four-day school week is a good idea that would benefit everyone. Schools should seriously consider making this change.",
    "proficiency_scores": {
      "Ideas": "Proficient",
      "Organization": "Proficient",
      "Voice": "Proficient",
      "Word Choice": "Approaching",
      "Sentence Fluency": "Approaching",
      "Conventions": "Approaching"
    },
    "persona_notes": {
      "grade_level": 8,
      "overall_level": "Proficient",
      "writing_strengths": ["Clear position statement", "Uses evidence to support claims", "Addresses counterargument"],
      "writing_weaknesses": ["Spelling errors (definately, Thats)", "Limited vocabulary range", "Some sentence structure repetition"],
      "error_patterns_applied": ["Misspelling of common words", "Missing apostrophes in contractions"]
    },
    "writing_traits": {
      "word_count": 198,
      "paragraph_count": 4,
      "average_sentence_length": 16.2,
      "tone": "Earnest and conversational"
    }
  },
  "metadata": {
    "model": "gemini-2.5-flash",
    "generation_time_ms": 3420,
    "template_used": "6-trait-writing",
    "request_id": "req_a1b2c3d4e5f6"
  }
}
```

**Response (400 Bad Request -- validation error):**

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid proficiency_level. Must be one of: Below, Approaching, Proficient, Exemplary.",
    "details": [
      {
        "field": "proficiency_level",
        "value": "Advanced",
        "allowed": ["Below", "Approaching", "Proficient", "Exemplary"]
      }
    ]
  }
}
```

**Response (500 Internal Server Error -- generation failed):**

```json
{
  "error": {
    "code": "GENERATION_FAILED",
    "message": "The model failed to generate a valid response after 2 attempts.",
    "details": [
      {
        "reason": "Response did not conform to expected JSON schema.",
        "model": "gemini-2.5-flash"
      }
    ]
  }
}
```

---

## Data Models

### Pydantic Request Models

```python
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class ProficiencyLevel(str, Enum):
    BELOW = "Below"
    APPROACHING = "Approaching"
    PROFICIENT = "Proficient"
    EXEMPLARY = "Exemplary"


class RubricDimensionLevel(BaseModel):
    Exemplary: str
    Proficient: str
    Approaching: str
    Below: str


class RubricDimension(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    levels: RubricDimensionLevel


class CustomRubric(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    dimensions: list[RubricDimension] = Field(..., min_length=1, max_length=10)


class PersonaConfig(BaseModel):
    error_patterns: list[str] = Field(default_factory=list, max_length=10)
    voice_traits: list[str] = Field(default_factory=list, max_length=10)


class GenerateRequest(BaseModel):
    assignment_prompt: str = Field(..., min_length=10, max_length=5000)
    proficiency_level: ProficiencyLevel
    rubric: Optional[CustomRubric] = None
    rubric_text: Optional[str] = Field(None, max_length=10000, description="Freeform rubric text pasted from an LMS or document. Parsed into structured format by the backend via Gemini.")
    template_id: Optional[str] = None
    grade_level: int = Field(default=8, ge=3, le=12)
    persona_config: Optional[PersonaConfig] = None
```

### Pydantic Response Models

```python
class ProficiencyScores(BaseModel):
    """Dynamic dict mapping rubric dimension names to proficiency levels."""
    scores: dict[str, ProficiencyLevel]


class PersonaNotes(BaseModel):
    grade_level: int
    overall_level: ProficiencyLevel
    writing_strengths: list[str]
    writing_weaknesses: list[str]
    error_patterns_applied: list[str]


class WritingTraits(BaseModel):
    word_count: int
    paragraph_count: int
    average_sentence_length: float
    tone: str


class GeneratedSample(BaseModel):
    student_response: str
    proficiency_scores: dict[str, str]
    persona_notes: PersonaNotes
    writing_traits: WritingTraits


class GenerationMetadata(BaseModel):
    model: str
    generation_time_ms: int
    template_used: Optional[str]
    request_id: str


class GenerateResponse(BaseModel):
    sample: GeneratedSample
    metadata: GenerationMetadata


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    model: str


class TemplateSummary(BaseModel):
    id: str
    name: str
    description: str
    grade_range: str
    dimensions: list[str]


class TemplatesListResponse(BaseModel):
    templates: list[TemplateSummary]


class ErrorDetail(BaseModel):
    field: Optional[str] = None
    value: Optional[str] = None
    allowed: Optional[list[str]] = None
    reason: Optional[str] = None
    model: Optional[str] = None


class ErrorBody(BaseModel):
    code: str
    message: str
    details: list[ErrorDetail] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    error: ErrorBody
```

---

## Notes for Implementation

1. **Request validation:** At least one of `template_id`, `rubric`, or `rubric_text` must be provided. Add a Pydantic `model_validator` to enforce this: if none is provided, return a 400. Resolution priority: `template_id` > `rubric` > `rubric_text`. When `rubric_text` is used, the backend sends the freeform text to Gemini with a parsing prompt to extract structured dimensions before proceeding with generation.

2. **CORS:** The FastAPI app must configure CORS middleware to allow requests from the Firebase Hosting domain and `localhost:5173` (Vite dev server).

3. **Request ID:** Generate a unique `request_id` per request using `uuid4()` prefixed with `req_`. This aids debugging in Cloud Run logs.

4. **Response times:** The `generation_time_ms` field measures only the Gemini API call duration, not total request processing time.
