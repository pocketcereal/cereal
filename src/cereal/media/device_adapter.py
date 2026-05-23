"""Device source adapter."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from cereal.media.uris import device_uri_index

if TYPE_CHECKING:
    from collections.abc import Callable

    from cereal.media.adapters import MediaCapture, OpenableMediaCapture
    from cereal.settings import SourceSettings

__all__ = ["DeviceSourceAdapter"]


@dataclass(frozen=True)
class DeviceSourceAdapter:
    """Opens capture device sources through an injected capture factory."""

    capture_factory: Callable[[int], OpenableMediaCapture]

    def open(self, source: SourceSettings) -> MediaCapture:
        """OpenCV capture expects a numeric index for local devices."""
        device_index = device_uri_index(source.uri)
        capture = self.capture_factory(device_index)
        if not capture.isOpened():
            msg = f"could not open media source: {source.uri}"
            raise RuntimeError(msg)
        return capture
