"""Default source adapter registry composition."""

from __future__ import annotations

from typing import TYPE_CHECKING

from cereal.media.adapters import SourceAdapterRegistry
from cereal.media.device_adapter import DeviceSourceAdapter
from cereal.media.file_adapter import FileSourceAdapter

if TYPE_CHECKING:
    from collections.abc import Callable

    from cereal.media.adapters import OpenableMediaCapture

__all__ = ["default_source_adapter_registry"]


def default_source_adapter_registry(
    capture_factory: Callable[[str | int], OpenableMediaCapture],
) -> SourceAdapterRegistry:
    """Compose Cereal's built-in Source adapters."""
    return SourceAdapterRegistry(
        {
            "file": FileSourceAdapter(capture_factory),
            "device": DeviceSourceAdapter(capture_factory),
        },
    )
