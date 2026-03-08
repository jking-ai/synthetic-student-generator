import json
import time
import uuid
from pathlib import Path

from app.config import settings
from app.models.requests import GenerateRequest, CustomRubric
from app.models.responses import (
    GenerateResponse,
    GeneratedSample,
    GenerationMetadata,
    TokenUsage,
)
from app.models.schemas import GENERATED_SAMPLE_SCHEMA
from app.services import gemini_client, prompt_builder, rubric_parser


_TEMPLATES_PATH = Path(__file__).resolve().parent.parent / "data" / "rubric_templates.json"
_templates: list[dict] | None = None


def _load_templates() -> list[dict]:
    global _templates
    if _templates is None:
        _templates = json.loads(_TEMPLATES_PATH.read_text(encoding="utf-8"))
    return _templates


def _get_template_by_id(template_id: str) -> dict | None:
    templates = _load_templates()
    for t in templates:
        if t["id"] == template_id:
            return t
    return None


def _rubric_to_detail(rubric: CustomRubric) -> dict:
    """Convert a CustomRubric pydantic model to a plain dict for prompt building."""
    return {
        "name": rubric.name,
        "dimensions": [
            {
                "name": dim.name,
                "levels": dim.levels.model_dump(),
            }
            for dim in rubric.dimensions
        ],
    }


async def generate_sample(request: GenerateRequest) -> GenerateResponse:
    """Orchestrate the full generation flow.

    Steps:
        1. Resolve rubric from template_id, custom rubric, or freeform text.
        2. Build system instruction and user prompt.
        3. Call Gemini for generation.
        4. Parse and validate the response.
        5. Return GenerateResponse with sample and metadata.

    Args:
        request: The validated GenerateRequest.

    Returns:
        A GenerateResponse containing the generated sample and metadata.

    Raises:
        ValueError: If template_id is invalid.
        gemini_client.GenerationError: If generation fails.
    """
    request_id = f"req_{uuid.uuid4().hex}"
    template_used: str | None = None
    start_time = time.time()

    # Step 1: Resolve rubric
    if request.template_id:
        template = _get_template_by_id(request.template_id)
        if template is None:
            raise ValueError(f"Invalid template_id: {request.template_id}")
        rubric_detail = template
        template_used = request.template_id
    elif request.rubric:
        rubric_detail = _rubric_to_detail(request.rubric)
    elif request.rubric_text:
        parsed_rubric = await rubric_parser.parse_rubric_text(request.rubric_text)
        rubric_detail = _rubric_to_detail(parsed_rubric)
    else:
        raise ValueError("No rubric source provided.")

    # Step 2: Build prompts
    persona_config_dict = None
    if request.persona_config:
        persona_config_dict = request.persona_config.model_dump()

    system_instruction = prompt_builder.build_system_instruction(
        rubric_detail=rubric_detail,
        proficiency_level=request.proficiency_level.value,
        grade_level=request.grade_level,
        persona_config=persona_config_dict,
    )
    user_prompt = prompt_builder.build_user_prompt(request.assignment_prompt)

    # Step 3: Call Gemini
    result = gemini_client.generate(
        system_instruction=system_instruction,
        user_prompt=user_prompt,
        response_schema=GENERATED_SAMPLE_SCHEMA,
    )

    # Step 4: Parse and validate
    sample = GeneratedSample(**result.content)

    # Step 5: Build token usage with cost estimate
    # Gemini 2.5 Flash pricing (per 1M tokens):
    #   Input: $0.15, Output: $0.60, Thinking: $0.35
    usage = result.usage
    token_usage = None
    if usage:
        cost = (
            usage.get("prompt_tokens", 0) * 0.15 / 1_000_000
            + usage.get("completion_tokens", 0) * 0.60 / 1_000_000
            + usage.get("thinking_tokens", 0) * 0.35 / 1_000_000
        )
        token_usage = TokenUsage(
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            thinking_tokens=usage.get("thinking_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
            estimated_cost_usd=round(cost, 6),
        )

    # Step 6: Build metadata and return
    elapsed_ms = int((time.time() - start_time) * 1000)

    metadata = GenerationMetadata(
        model=settings.GEMINI_MODEL,
        generation_time_ms=elapsed_ms,
        template_used=template_used,
        request_id=request_id,
        token_usage=token_usage,
    )

    return GenerateResponse(sample=sample, metadata=metadata)
