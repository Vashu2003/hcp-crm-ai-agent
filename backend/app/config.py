from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App configuration loaded from environment / .env file."""

    groq_api_key: str = ""
    groq_model: str = "gemma2-9b-it"
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/aivoa_crm"
    frontend_origin: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
