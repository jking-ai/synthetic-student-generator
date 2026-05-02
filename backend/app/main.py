from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.rate_limit import limiter
from app.routers import generate, health, templates


def _rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Return a clear JSON 429 when an IP exceeds a configured rate limit."""
    return JSONResponse(
        status_code=429,
        content={
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": (
                    "Too many requests. This endpoint is rate-limited per IP "
                    "to protect against cost-runaway abuse. Please slow down "
                    "and try again shortly."
                ),
                "limit": str(exc.detail),
            }
        },
    )


def create_app() -> FastAPI:
    docs_enabled = settings.DOCS_ENABLED
    application = FastAPI(
        title="Synthetic Student Generator API",
        version="1.0.0",
        # Hide interactive docs in production; portfolio service does not need
        # a public OpenAPI explorer surface.
        docs_url="/docs" if docs_enabled else None,
        redoc_url="/redoc" if docs_enabled else None,
        openapi_url="/openapi.json" if docs_enabled else None,
    )

    # Wire slowapi into the app so @limiter.limit decorators take effect and
    # 429s render as our JSON shape rather than slowapi's default text.
    application.state.limiter = limiter
    application.add_exception_handler(RateLimitExceeded, _rate_limit_handler)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(health.router, prefix="/api/v1")
    application.include_router(templates.router, prefix="/api/v1")
    application.include_router(generate.router, prefix="/api/v1")

    @application.get("/")
    async def root_redirect():
        return RedirectResponse(url="/api/v1/health")

    return application


app = create_app()
