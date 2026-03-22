from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Корень проекта (папка backend), чтобы .env находился при любом cwd
_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_ENV_FILE = _BACKEND_ROOT / ".env"


class Settings(BaseSettings):
    """Все секреты и URL — только из переменных окружения / .env (см. .env.example)."""

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Database (единственное место для строки подключения)
    DATABASE_URL: str = Field(
        ...,
        description="SQLAlchemy async URL, например postgresql+asyncpg://user:pass@host:5432/db",
    )

    # Redis
    REDIS_URL: str = Field(..., description="redis://host:6379/0")

    # JWT
    SECRET_KEY: str = Field(..., min_length=16, description="Секрет для подписи JWT")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # App
    APP_NAME: str = "Messenger"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # CORS: через запятую, без пробелов или с пробелами — обрежутся в main
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="Разрешённые origin для CORS, через запятую",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
