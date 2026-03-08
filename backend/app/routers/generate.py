from fastapi import APIRouter, HTTPException

from app.models.requests import GenerateRequest
from app.models.responses import GenerateResponse
from app.services.gemini_client import GenerationError
from app.services.generator import generate_sample

router = APIRouter()


@router.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest) -> GenerateResponse:
    try:
        return await generate_sample(request)
    except ValueError as exc:
        # Invalid template_id or missing rubric source
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "INVALID_TEMPLATE_ID",
                    "message": str(exc),
                }
            },
        )
    except GenerationError as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "GENERATION_FAILED",
                    "message": str(exc),
                }
            },
        )
