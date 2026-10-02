import os
from pathlib import Path
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseModel as BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent

class PlatformSettings(BaseSettings):
    PROJECT_NAME: str = "Age-Aware Advertisement Platform"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "ageaware_adplatform_jwt_secret_key_2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'backend' / 'safead.db'}")
    
    # Storage Paths
    UPLOAD_DIR: Path = BASE_DIR / "assets" / "uploads"
    SAMPLE_MEDIA_DIR: Path = BASE_DIR / "assets" / "sample_media"
    
    # Remote AI inference (Optional)
    COLAB_API_URL: str = os.getenv("COLAB_API_URL", "")
    
    # Server network settings
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "127.0.0.1")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    FRONTEND_PORT: int = int(os.getenv("FRONTEND_PORT", "8501"))
    
    # 4 Standard Application Ad Categories
    AD_CATEGORIES: list = [
        "SAFE FOR ALL",
        "14+",
        "18+",
        "UNSAFE FOR ALL"
    ]
    
    # 3 Standard User Age Categories
    USER_AGE_CATEGORIES: list = [
        "SAFE FOR ALL",
        "14+",
        "18+"
    ]
    
    # Mapping from backend internal enum to application display category
    BACKEND_TO_APP_MAP: dict = {
        "SAFE_FOR_ALL": "SAFE FOR ALL",
        "SAFE_14_PLUS": "14+",
        "SAFE_18_PLUS": "18+",
        "UNSAFE_FOR_ALL": "UNSAFE FOR ALL",
        "REQUIRES_HUMAN_REVIEW": "UNSAFE FOR ALL"  # Until approved
    }
    
    # Mapping from application category to backend internal enum
    APP_TO_BACKEND_MAP: dict = {
        "SAFE FOR ALL": "SAFE_FOR_ALL",
        "14+": "SAFE_14_PLUS",
        "18+": "SAFE_18_PLUS",
        "UNSAFE FOR ALL": "UNSAFE_FOR_ALL"
    }

    # Delivery eligibility mapping: User Category -> Allowed Ad Categories
    DELIVERY_ELIGIBILITY: dict = {
        "SAFE FOR ALL": ["SAFE FOR ALL"],
        "14+": ["SAFE FOR ALL", "14+"],
        "18+": ["SAFE FOR ALL", "14+", "18+"]
    }
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = PlatformSettings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
