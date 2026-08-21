import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./data/resumes.db"
    
    # Gemini API
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", "")
    
    # Model settings - Use gemini-pro instead of gemini-1.5-flash
    MODEL_NAME: str = "all-MiniLM-L6-v2"
    SPACY_MODEL: str = "en_core_web_sm"
    GEMINI_MODEL: str = "gemini-pro"  # Updated to the correct model name
    
    # Matching weights
    SKILL_WEIGHT: float = 0.5
    EXPERIENCE_WEIGHT: float = 0.3
    EDUCATION_WEIGHT: float = 0.2
    
    # Thresholds
    SHORTLIST_THRESHOLD: float = 0.70
    
    # File upload settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS: list = [".pdf", ".txt"]
    
    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()