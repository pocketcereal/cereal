"""Runtime settings for Cereal."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_settings import (
    BaseSettings,
    CliSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

DEFAULT_CONFIG_PATH = Path("config/settings.yaml")


class SourceSettings(BaseModel):
    """Typed configuration for one Cereal source."""

    name: str = Field(pattern=r"^[a-z0-9_]+$")
    uri: str
    label: str | None = None
    write: bool = False

    model_config = ConfigDict(frozen=True)

    @field_validator("uri")
    @classmethod
    def require_uri_scheme(cls, value: str) -> str:
        """Require URI-shaped source locators without restricting schemes."""
        parsed = urlparse(value)
        if not parsed.scheme:
            msg = "source uri must include a scheme"
            raise ValueError(msg)
        return value


class Settings(BaseSettings):
    """Typed runtime configuration for Cereal."""

    storage: Path
    sources: list[SourceSettings] = Field(min_length=1)

    model_config = SettingsConfigDict(
        yaml_file=DEFAULT_CONFIG_PATH,
        extra="ignore",
        frozen=True,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Load settings through pydantic-settings YAML support."""
        del init_settings, env_settings, dotenv_settings, file_secret_settings
        return (YamlConfigSettingsSource(settings_cls),)


class ConfigSelection(BaseSettings):
    """Configuration-file selection from operational inputs."""

    config_path: Path = DEFAULT_CONFIG_PATH

    model_config = SettingsConfigDict(
        cli_shortcuts={"config_path": "config"},
        extra="ignore",
    )


def load_settings(config_path: Path | None = None) -> Settings:
    """Load settings from the selected YAML config."""
    resolved_path = config_path or DEFAULT_CONFIG_PATH
    if not resolved_path.exists():
        msg = f"configuration file not found: {resolved_path}"
        raise FileNotFoundError(msg)

    values: dict[str, Any] = {}
    return _settings_type(resolved_path)(**values)


def select_config_path(args: Sequence[str] | None = None) -> Path:
    """Select the YAML config path from CLI args or the default."""
    cli_parse_args: bool | list[str] = True if args is None else list(args)
    cli_values = CliSettingsSource(ConfigSelection, cli_parse_args=cli_parse_args)()
    return ConfigSelection.model_validate(cli_values).config_path


def _settings_type(config_path: Path) -> type[Settings]:
    config = dict(Settings.model_config)
    config["yaml_file"] = config_path

    class ConfiguredSettings(Settings):
        model_config = SettingsConfigDict(**config)

    return ConfiguredSettings
