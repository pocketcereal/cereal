"""Runtime settings for Cereal."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed runtime configuration for Cereal."""

    app_name: str = "cereal"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="CEREAL_",
        extra="ignore",
    )


def load_settings() -> Settings:
    """Load settings from defaults, environment variables, and `.env`."""
    return Settings()
