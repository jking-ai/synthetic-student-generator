from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.config import settings
from app.routers import health, templates, generate


def create_app() -> FastAPI:
    application = FastAPI(
        title="Synthetic Student Generator API",
        version="1.0.0",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_ORIGIN],
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
