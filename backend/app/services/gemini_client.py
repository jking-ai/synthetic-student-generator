import json

from google import genai
from google.genai import types

from app.config import settings


class GenerationError(Exception):
    """Raised when Gemini generation fails."""

    def __init__(self, message: str, cause: Exception | None = None):
        super().__init__(message)
        self.cause = cause


_client = genai.Client(
    vertexai=True,
    project=settings.GCP_PROJECT_ID,
    location=settings.GCP_REGION,
)


class GenerateResult:
    """Container for generation output and token usage."""

    def __init__(self, content: dict, usage: dict):
        self.content = content
        self.usage = usage


def generate(
    system_instruction: str,
    user_prompt: str,
    response_schema: dict,
) -> GenerateResult:
    """Send a generation request to Gemini and return parsed JSON with usage metadata.

    Args:
        system_instruction: The system prompt guiding the model's behavior.
        user_prompt: The user-facing prompt (assignment text).
        response_schema: A JSON Schema dict for structured output.

    Returns:
        GenerateResult with parsed content dict and token usage dict.

    Raises:
        GenerationError: If generation or parsing fails.
    """
    try:
        response = _client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=response_schema,
            ),
        )

        if not response.text:
            raise GenerationError("Gemini returned an empty response.")

        content = json.loads(response.text)

        # Extract token usage from response metadata
        usage = {}
        um = response.usage_metadata
        if um:
            usage = {
                "prompt_tokens": um.prompt_token_count or 0,
                "completion_tokens": um.candidates_token_count or 0,
                "thinking_tokens": um.thoughts_token_count or 0,
                "total_tokens": um.total_token_count or 0,
            }

        return GenerateResult(content=content, usage=usage)

    except json.JSONDecodeError as exc:
        raise GenerationError(
            f"Failed to parse Gemini response as JSON: {exc}", cause=exc
        )
    except GenerationError:
        raise
    except Exception as exc:
        raise GenerationError(
            f"Gemini generation failed: {exc}", cause=exc
        )
