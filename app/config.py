from pydantic_settings import BaseSettings
from pydantic import EmailStr, Field


class Settings(BaseSettings):
    app_name: str = "LLM Analysis Quiz"
    email: EmailStr = Field(..., alias="APP_EMAIL")
    secret: str = Field(..., alias="APP_SECRET")

    openai_api_key: str | None = Field(None, alias="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4.1-mini", alias="OPENAI_MODEL")

    max_quiz_depth: int = Field(5, alias="MAX_QUIZ_DEPTH")
    request_timeout_seconds: int = Field(55, alias="REQUEST_TIMEOUT_SECONDS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
