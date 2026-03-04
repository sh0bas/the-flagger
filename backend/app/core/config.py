"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Application
    PROJECT_NAME: str = "Flagger"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    model_config = SettingsConfigDict(
        env_file=["../.env", ".env"],
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
