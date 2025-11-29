# app/config.py
from functools import lru_cache
from pydantic_settings import BaseSettings  # <-- changed import


class Settings(BaseSettings):
    app_name: str = "LLM Analysis Quiz Solver"

    # Required for evaluation
    email: str
    secret: str

    # LLM configuration
    llm_api_key: str
    llm_model: str = "gpt-4.1-mini"
    llm_base_url: str | None = None

    # HTTP / runtime settings
    http_timeout: int = 60
    max_payload_bytes: int = 1_000_000
    log_level: str = "INFO"
    user_agent: str = "TDS-LLM-Analysis-Quiz-Bot/1.0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
