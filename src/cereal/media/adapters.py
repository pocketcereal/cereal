"""Source adapter dispatch."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from cereal.media.uris import source_uri_scheme

if TYPE_CHECKING:
    from cereal.settings import SourceSettings

__all__ = ["MediaCapture", "OpenableMediaCapture", "SourceAdapter", "SourceAdapterRegistry"]


class MediaCapture(Protocol):
    """Readable media resource that must be released by the preview loop."""

    def read(self) -> tuple[bool, object | None]:
        """Read the next frame if one is available."""

    def release(self) -> None:
        """Release the underlying media resource."""


class OpenableMediaCapture(MediaCapture, Protocol):
    """OpenCV-shaped capture that can report whether opening succeeded."""

    def isOpened(self) -> bool:  # noqa: N802
        """Return whether the underlying media resource opened."""


class SourceAdapter(Protocol):
    """Runtime adapter for one source URI scheme."""

    def open(self, source: SourceSettings) -> MediaCapture:
        """Open a configured source."""


@dataclass(frozen=True)
class SourceAdapterRegistry:
    """Maps source URI schemes to runtime adapters."""

    adapters: dict[str, SourceAdapter]

    def adapter_for(self, source: SourceSettings) -> SourceAdapter:
        """Select the adapter for a configured source."""
        return self.adapters[source_uri_scheme(source.uri)]
