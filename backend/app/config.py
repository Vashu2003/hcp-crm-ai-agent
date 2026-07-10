from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App configuration loaded from environment / .env file."""

    groq_api_key: str = ""
    # Model is configurable via GROQ_MODEL. The assignment's primary (gemma2-9b-it)
    # was decommissioned by Groq. We default to llama-3.1-8b-instant (small, fast,
    # gemma-class) to stay within Groq's free-tier daily token budget; set
    # GROQ_MODEL=llama-3.3-70b-versatile (the assignment's alternative) for higher
    # quality if your account has the token headroom.
    groq_model: str = "llama-3.1-8b-instant"
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/aivoa_crm"
    frontend_origin: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
