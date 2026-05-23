"""File source adapter."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from cereal.media.uris import file_uri_path

if TYPE_CHECKING:
    from collections.abc import Callable

    from cereal.media.adapters import MediaCapture, OpenableMediaCapture
    from cereal.settings import SourceSettings

__all__ = ["FileSourceAdapter"]


@dataclass(frozen=True)
class FileSourceAdapter:
    """Opens local file sources through an injected capture factory."""

    capture_factory: Callable[[str], OpenableMediaCapture]

    def open(self, source: SourceSettings) -> MediaCapture:
        """OpenCV capture needs a filesystem path, not a file URI."""
        source_path = file_uri_path(source.uri)
        capture = self.capture_factory(str(source_path))
        if not capture.isOpened():
            msg = f"could not open media source: {source_path}"
            raise RuntimeError(msg)
        return capture
