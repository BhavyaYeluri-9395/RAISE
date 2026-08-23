import os
from pathlib import Path
from typing import Optional


class Settings:
    # ============================================================
    # Database
    # ============================================================

    DATABASE_URL: str = "sqlite:///./data/resumes.db"


    # ============================================================
    # Gemini API
    # ============================================================

    GEMINI_API_KEY: Optional[str] = None


    # ============================================================
    # Authentication / JWT
    # ============================================================

    AUTH_SECRET_KEY: Optional[str] = None
    AUTH_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


    # ============================================================
    # Models
    # ============================================================

    MODEL_NAME: str = "all-MiniLM-L6-v2"
    SPACY_MODEL: str = "en_core_web_sm"


    # ============================================================
    # Matching
    # ============================================================

    SKILL_WEIGHT: float = 0.5
    EXPERIENCE_WEIGHT: float = 0.3
    EDUCATION_WEIGHT: float = 0.2

    SHORTLIST_THRESHOLD: float = 0.70


    # ============================================================
    # File Upload
    # ============================================================

    MAX_FILE_SIZE: int = 10 * 1024 * 1024

    ALLOWED_EXTENSIONS: list = [
        ".pdf",
        ".txt"
    ]


# ================================================================
# Load .env
# ================================================================

try:

    from dotenv import load_dotenv

    # Project root:
    # D:\Projects\smart-resume-screener-main\.env

    env_path = Path(__file__).parent.parent.parent / ".env"

    if env_path.exists():

        load_dotenv(env_path)

        print(f"Loaded .env from: {env_path}")

    else:

        load_dotenv(".env")

        print("Loaded .env from current directory")


    # ============================================================
    # Gemini API Key
    # ============================================================

    Settings.GEMINI_API_KEY = os.getenv(
        "GEMINI_API_KEY"
    )

    if Settings.GEMINI_API_KEY:

        print(
            f"Gemini API key loaded "
            f"(starts with: {Settings.GEMINI_API_KEY[:8]}...)"
        )

    else:

        print("Gemini API key not found")


    # ============================================================
    # Authentication Settings
    # ============================================================

    Settings.AUTH_SECRET_KEY = os.getenv(
        "SECRET_KEY"
    )

    Settings.AUTH_ALGORITHM = os.getenv(
        "AUTH_ALGORITHM",
        "HS256"
    )

    Settings.ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv(
            "ACCESS_TOKEN_EXPIRE_MINUTES",
            "60"
        )
    )


    # Authentication status

    if Settings.AUTH_SECRET_KEY:

        print("Authentication secret key loaded")

    else:

        print(
            "WARNING: Authentication secret key not found"
        )


except Exception as e:

    print(f"Could not load .env: {e}")


# ================================================================
# Settings Instance
# ================================================================

settings = Settings()