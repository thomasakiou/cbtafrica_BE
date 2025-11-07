from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "CBT Backend"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8002
    WORKERS: int = 1
    
    # API
    API_V1_STR: str = "/api/v1"
    ROOT_PATH: str = ""  # This will be set to "/cbt" when behind Nginx
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost/cbt_db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
