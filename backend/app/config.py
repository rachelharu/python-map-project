from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = Field(validation_alias="DATABASE_URL")
    census_api_key: str | None = Field(default=None, validation_alias="CENSUS_API_KEY")

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / ".env",
        case_sensitive=False,
        extra="ignore",
    )

settings = Settings()
