"""Source selection for media runtime paths."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cereal.media.adapters import MediaCapture, SourceAdapterRegistry
    from cereal.settings import Settings, SourceSettings

__all__ = ["first_configured_source", "open_first_configured_source"]


def first_configured_source(settings: Settings) -> SourceSettings:
    """Phase one previews a single configured source."""
    return settings.sources[0]


def open_first_configured_source(
    settings: Settings,
    registry: SourceAdapterRegistry,
) -> MediaCapture:
    """Phase-one media startup opens only the first configured source."""
    source = first_configured_source(settings)
    return registry.adapter_for(source).open(source)
