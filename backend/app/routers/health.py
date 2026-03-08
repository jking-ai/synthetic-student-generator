from fastapi import APIRouter

from app.config import settings
from app.models.responses import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        service="synthetic-student-generator",
        version="1.0.0",
        model=settings.GEMINI_MODEL,
    )
