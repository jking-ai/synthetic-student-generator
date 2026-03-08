from pydantic import BaseModel, Field, model_validator
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
    rubric_text: Optional[str] = Field(None, max_length=10000)
    template_id: Optional[str] = None
    grade_level: int = Field(default=8, ge=3, le=12)
    persona_config: Optional[PersonaConfig] = None

    @model_validator(mode="after")
    def check_rubric_source(self):
        if not self.template_id and not self.rubric and not self.rubric_text:
            raise ValueError(
                "At least one of template_id, rubric, or rubric_text must be provided"
            )
        return self
