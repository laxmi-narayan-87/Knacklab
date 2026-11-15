import sys
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    port: int = Field(default=8000)
    database_url: str | None = None
    mongodb_uri: str | None = None
    redis_url: str | None = None
    jwt_secret: str | None = None
    api_key_a: str | None = None
    api_key_b: str | None = None

    @field_validator("port", mode="before")
    @classmethod
    def validate_port_value(cls, v):
        if v is None or str(v).strip() == "":
            raise ValueError("PORT cannot be blank. Set a valid numeric PORT in .env (example: PORT=8000).")
        try:
            val = int(v)
        except (TypeError, ValueError):
            raise ValueError(f"Invalid PORT: '{v}'. PORT must be a valid integer.")
        if val <= 0 or val > 65535:
            raise ValueError(f"Invalid PORT: {val}. PORT must be between 1 and 65535.")
        return val

def get_settings() -> Settings:
    try:
        return Settings()
    except Exception as exc:
        sys.stderr.write(f"\n[FATAL] Startup Configuration Error: {exc}\n")
        raise exc

settings = get_settings()
