from pydantic import BaseModel
from typing import Optional

from app.models.requests import ProficiencyLevel


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


class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    thinking_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0


class GenerationMetadata(BaseModel):
    model: str
    generation_time_ms: int
    template_used: Optional[str] = None
    request_id: str
    token_usage: Optional[TokenUsage] = None


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
    code: str
    message: str


class ErrorBody(BaseModel):
    error: ErrorDetail


class ErrorResponse(BaseModel):
    detail: ErrorBody
