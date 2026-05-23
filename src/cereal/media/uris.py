"""Source URI helpers."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import unquote, urlparse

__all__ = ["device_uri_index", "file_uri_path", "source_uri_scheme"]


def device_uri_index(uri: str) -> int:
    """Convert a device URI into an OpenCV capture device index."""
    parsed = urlparse(uri)
    return int(parsed.path)


def file_uri_path(uri: str) -> Path:
    """Convert a local file URI into the path expected by media backends."""
    parsed = urlparse(uri)
    return Path(unquote(parsed.path))


def source_uri_scheme(uri: str) -> str:
    """Return the scheme used for Source adapter lookup."""
    return urlparse(uri).scheme
