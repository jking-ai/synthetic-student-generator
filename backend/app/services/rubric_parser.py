import json

from google.genai import types

from app.models.requests import CustomRubric
from app.services.gemini_client import _client, GenerationError
from app.config import settings


_PARSER_SYSTEM_INSTRUCTION = """You are a rubric parsing assistant. Given freeform rubric text, extract it into a structured format.

Extract:
1. A short rubric name summarizing the rubric's purpose.
2. The scoring dimensions (criteria). Each dimension needs:
   - A name (short label)
   - Four proficiency level descriptors:
     - Exemplary: The highest level of performance
     - Proficient: Meets expectations
     - Approaching: Partially meets expectations
     - Below: Does not yet meet expectations

If the rubric text uses different level names (e.g., "Advanced", "Basic"), map them to Exemplary/Proficient/Approaching/Below in descending order.

If a level descriptor is not explicitly provided in the text, write a reasonable descriptor that fits between the levels that are provided."""

_PARSER_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "dimensions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "levels": {
                        "type": "object",
                        "properties": {
                            "Exemplary": {"type": "string"},
                            "Proficient": {"type": "string"},
                            "Approaching": {"type": "string"},
                            "Below": {"type": "string"},
                        },
                        "required": [
                            "Exemplary",
                            "Proficient",
                            "Approaching",
                            "Below",
                        ],
                    },
                },
                "required": ["name", "levels"],
            },
        },
    },
    "required": ["name", "dimensions"],
}


async def parse_rubric_text(rubric_text: str) -> CustomRubric:
    """Parse freeform rubric text into a structured CustomRubric using Gemini.

    Args:
        rubric_text: The raw rubric text from the user.

    Returns:
        A validated CustomRubric model.

    Raises:
        GenerationError: If parsing fails.
    """
    try:
        response = _client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=f"Parse the following rubric text into structured dimensions:\n\n{rubric_text}",
            config=types.GenerateContentConfig(
                system_instruction=_PARSER_SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=_PARSER_RESPONSE_SCHEMA,
            ),
        )

        if not response.text:
            raise GenerationError("Gemini returned an empty response when parsing rubric.")

        parsed = json.loads(response.text)
        return CustomRubric(**parsed)

    except json.JSONDecodeError as exc:
        raise GenerationError(
            f"Failed to parse rubric parsing response as JSON: {exc}", cause=exc
        )
    except GenerationError:
        raise
    except Exception as exc:
        raise GenerationError(
            f"Rubric parsing failed: {exc}", cause=exc
        )
