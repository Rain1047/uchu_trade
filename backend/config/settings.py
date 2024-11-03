from pathlib import Path
from pydantic import BaseModel, Field
from typing import List
from functools import lru_cache
import os

# 打印当前工作目录和文件位置
print("Current working directory:", os.getcwd())
print("Settings file location:", Path(__file__).absolute())


class Settings(BaseModel):
    # Environment
    ENV: str = "development"
    DEBUG: bool = True

    # API Settings
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000

    # CORS Settings
    ALLOWED_ORIGINS: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:8080",
            "http://127.0.0.1:3000"
        ]
    )
    ALLOWED_METHODS: List[str] = Field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    ALLOWED_HEADERS: List[str] = Field(default_factory=lambda: [
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With"
    ])
    CORS_MAX_AGE: int = 600

    RATE_LIMIT: str = "100/hour"  # 根据需要设置默认值

    ALLOWED_HOSTS: str = "localhost,127.0.0.1"

    RATE_LIMIT_ENABLED: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

    @property
    def cors_origins(self) -> List[str]:
        if self.ENV == "production":
            return self.ALLOWED_ORIGINS
        return [str(origin) for origin in self.ALLOWED_ORIGINS]


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

if __name__ == '__main__':
    print(f"ALLOWED_ORIGINS: {settings.ALLOWED_ORIGINS}")
