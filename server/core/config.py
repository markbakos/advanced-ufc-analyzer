from pydantic.v1 import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """Server settings"""

    API_PREFIX: str = "/api"
    PROJECT_NAME: str = "UFC Fight Prediction"
    PROJECT_DESCRIPTION: str = "API for UFC Fight Prediction"
    VERSION: str = "1.0.0"

    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 1 day
    ALGORITHM = "HS256"
    JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()