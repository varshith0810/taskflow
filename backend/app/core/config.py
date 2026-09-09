import os
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "TaskFlow"
    APP_VERSION: str = "1.0.0"
    DATABASE_URL: str = "sqlite:///./task_manager.db"
    SECRET_KEY: str = "dev-secret-key-change-in-production-please"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    @field_validator("SECRET_KEY")
    def validate_secret_key(cls, v: str, info):
        env = str(info.data.get("ENVIRONMENT", "development")).lower()
        if env == "production" and v == "dev-secret-key-change-in-production-please":
            raise ValueError("Insecure default SECRET_KEY cannot be used in production!")
        return v

    @property
    def origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    def validate_production_secrets(self) -> None:
        """Prevent deployment with default development keys in production."""
        is_prod = self.ENVIRONMENT.lower() == "production"
        if is_prod and self.SECRET_KEY == "dev-secret-key-change-in-production-please":
            raise ValueError(
                "🚨 CRITICAL SECURITY ERROR: The default SECRET_KEY cannot be used in production! "
                "Set a secure 32+ byte random SECRET_KEY in your environment variables."
            )

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
settings.validate_production_secrets()