import os
from typing import List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings


_DEFAULT_ALLOWED_ORIGINS = (
    "https://synthetic-student-gen.web.app,"
    "https://synthetic-student-gen.firebaseapp.com,"
    "http://localhost:5173"
)


class Settings(BaseSettings):
    GCP_PROJECT_ID: str = "your-gcp-project-id"
    GCP_REGION: str = "us-central1"
    GEMINI_LOCATION: str = "global"
    GEMINI_MODEL: str = "gemini-3.1-pro-preview"
    # Comma-separated list of origins allowed by CORS. Production defaults
    # cover the deployed Firebase Hosting URLs plus the local dev server.
    ALLOWED_ORIGINS: str = _DEFAULT_ALLOWED_ORIGINS
    # Whether to expose FastAPI's interactive docs (/docs, /redoc, openapi.json).
    # Defaults to False so production is locked down; flip to True for local dev.
    DOCS_ENABLED: bool = False
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        # Tolerate stale keys (e.g. legacy FRONTEND_ORIGIN) in a developer's
        # local .env so removing/renaming a setting doesn't crash the app.
        "extra": "ignore",
    }

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parsed list of CORS origins (comma-separated string -> trimmed list)."""
        return [
            origin.strip()
            for origin in self.ALLOWED_ORIGINS.split(",")
            if origin.strip()
        ]


settings = Settings()

# Ensure GOOGLE_APPLICATION_CREDENTIALS is set in the OS environment for local dev.
# The google-genai SDK reads os.environ, not pydantic settings.
# On Cloud Run, ADC is provided by the service account identity — no key file needed.
if settings.GOOGLE_APPLICATION_CREDENTIALS:
    creds_path = settings.GOOGLE_APPLICATION_CREDENTIALS
    if os.path.isfile(creds_path) and not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
