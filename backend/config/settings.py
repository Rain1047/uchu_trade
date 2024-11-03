from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    # Environment
    ENV: str = "development"
    DEBUG: bool = True

    # API Settings
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000

    # CORS Settings
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    ALLOWED_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    ALLOWED_HEADERS: List[str] = [
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With"
    ]
    CORS_MAX_AGE: int = 600

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT: str = "100/minute"

    class Config:
        env_file = ".env"

    @property
    def cors_origins(self) -> List[str]:
        if self.ENV == "production":
            return self.ALLOWED_ORIGINS
        return [str(origin) for origin in self.ALLOWED_ORIGINS]


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
