"""Tests for Cereal settings."""

from cereal.settings import Settings


def test_default_settings_have_app_name() -> None:
    """Default settings include a non-empty app name."""
    assert Settings().app_name
