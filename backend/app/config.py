import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GCP_PROJECT_ID: str = "your-gcp-project-id"
    GCP_REGION: str = "us-central1"
    GEMINI_MODEL: str = "gemini-2.5-flash"
    FRONTEND_ORIGIN: str = "http://localhost:5173"
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


settings = Settings()

# Ensure GOOGLE_APPLICATION_CREDENTIALS is set in the OS environment for local dev.
# The google-genai SDK reads os.environ, not pydantic settings.
# On Cloud Run, ADC is provided by the service account identity — no key file needed.
if settings.GOOGLE_APPLICATION_CREDENTIALS:
    creds_path = settings.GOOGLE_APPLICATION_CREDENTIALS
    if os.path.isfile(creds_path) and not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
