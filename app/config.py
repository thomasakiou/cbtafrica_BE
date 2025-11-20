from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):

    # Application
    APP_NAME: str = "CBT Africa Application API"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8002
    WORKERS: int = 1
    
    # API
    API_V1_STR: str = "/api/v1"
    ROOT_PATH: str = "/cbt"  # This will be set to "/cbt" when behind Nginx
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000",
                                       "https://cbtafrica.netlify.app/",
                                       "http://127.0.0.1:5500/"]

    # Database
    DATABASE_URL: str = "postgresql://thomas:ebimobowei81@localhost:5432/cbt_db"
    
    # Security
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"
    
    # File Upload Settings
    UPLOAD_DIR: str = "uploads/explanation_images"
    QUESTION_IMAGE_DIR: str = "uploads/question_images"
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB in bytes
    ALLOWED_IMAGE_EXTENSIONS: list[str] = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
    
    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
