from pydantic.v1 import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Server settings"""

    API_PREFIX: str = "/api"
    PROJECT_NAME: str = "UFC Fight Prediction"
    PROJECT_DESCRIPTION: str = "API for UFC Fight Prediction"
    VERSION: str = "1.0.0"

    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()