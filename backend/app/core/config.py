import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Ensure .env is explicitly loaded from project root
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))
load_dotenv(dotenv_path, override=True)

class Settings(BaseSettings):
    PROJECT_NAME: str = "SafeAd AI (SAFE-VISION)"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "safead_ai_jwt_secret_key_change_in_production_2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./safead.db")
    
    # Colab Inference API URL
    COLAB_API_URL: str = os.getenv("COLAB_API_URL", "")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
