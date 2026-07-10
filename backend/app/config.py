from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App configuration loaded from environment / .env file."""

    groq_api_key: str = ""
    # Model is configurable via GROQ_MODEL. The assignment's primary (gemma2-9b-it)
    # was decommissioned by Groq. We default to openai/gpt-oss-20b: reliable at
    # tool-calling and comfortable within the free-tier token budget. Set
    # GROQ_MODEL=llama-3.3-70b-versatile (the assignment's listed alternative) for
    # higher quality if your account has the daily token headroom.
    groq_model: str = "openai/gpt-oss-20b"
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/aivoa_crm"
    frontend_origin: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
