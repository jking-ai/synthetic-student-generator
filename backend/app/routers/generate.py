from fastapi import APIRouter, HTTPException, Request

from app.models.requests import GenerateRequest
from app.models.responses import GenerateResponse
from app.rate_limit import GENERATE_LIMITS, limiter
from app.services.gemini_client import GenerationError
from app.services.generator import generate_sample

router = APIRouter()


# Rate limit: 5/minute, 50/day per client IP. This endpoint hits Gemini 3.1 Pro
# (~$2/$12 per 1M input/output tokens) so unrestricted access on a public Cloud
# Run URL is a real cost-runaway risk. See app/rate_limit.py for the IP key fn.
@router.post("/generate", response_model=GenerateResponse)
@limiter.limit(GENERATE_LIMITS[0])
@limiter.limit(GENERATE_LIMITS[1])
async def generate(request: Request, payload: GenerateRequest) -> GenerateResponse:
    try:
        return await generate_sample(payload)
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
