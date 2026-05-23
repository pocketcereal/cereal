"""OpenCV-backed preview boundary for Cereal.

OpenCV is loaded lazily so importing the media boundary stays cheap.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from types import ModuleType

    from cereal.media.adapters import MediaCapture, OpenableMediaCapture
    from cereal.settings import Settings

from cereal.media.registry import default_source_adapter_registry
from cereal.media.sources import open_first_configured_source

__all__ = ["PreviewBackend", "load_opencv", "run_preview", "run_preview_loop"]


@dataclass(frozen=True)
class PreviewBackend:
    """Window operations for the preview loop."""

    show_frame: Callable[[str, object], None]
    should_stop: Callable[[str, int], bool]
    destroy_windows: Callable[[], None]


def load_opencv() -> ModuleType:  # noqa: D103
    import cv2  # noqa: PLC0415

    return cv2


def _opencv_preview_backend(opencv: ModuleType) -> PreviewBackend:
    return PreviewBackend(
        show_frame=opencv.imshow,
        should_stop=lambda window_name, delay_ms: (
            opencv.waitKey(delay_ms) == ord("q")
            or opencv.getWindowProperty(window_name, opencv.WND_PROP_VISIBLE) < 1
        ),
        destroy_windows=opencv.destroyAllWindows,
    )


def run_preview(
    settings: Settings,
    *,
    capture_factory: Callable[[str | int], OpenableMediaCapture] | None = None,
    backend: PreviewBackend | None = None,
) -> None:
    """Open the first configured source and run the preview loop."""
    opencv = None
    if capture_factory is None:
        opencv = load_opencv()
        capture_factory = opencv.VideoCapture

    registry = default_source_adapter_registry(capture_factory)
    capture = open_first_configured_source(settings, registry)
    run_preview_loop(capture, backend or _opencv_preview_backend(opencv or load_opencv()))


def run_preview_loop(
    capture: MediaCapture,
    backend: PreviewBackend,
    *,
    window_name: str = "Cereal Preview",
    delay_ms: int = 33,
) -> None:
    """Display frames until EOF, user quit, or window close."""
    try:
        while True:
            has_frame, frame = capture.read()
            if not has_frame:
                break

            backend.show_frame(window_name, frame)
            if backend.should_stop(window_name, delay_ms):
                break
    finally:
        capture.release()
        backend.destroy_windows()
