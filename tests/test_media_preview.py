"""Tests for the Cereal media preview boundary."""

from __future__ import annotations

import importlib
from types import ModuleType
from typing import TYPE_CHECKING

from cereal.media.preview import PreviewBackend, run_preview, run_preview_loop
from cereal.settings import load_settings
from tests.helpers import write_config

if TYPE_CHECKING:
    from pathlib import Path


def test_preview_module_is_importable() -> None:
    """The preview backend lives behind a dedicated media module boundary."""
    preview_module = importlib.import_module("cereal.media.preview")

    assert isinstance(preview_module, ModuleType)


def test_preview_loop_shows_frames_until_end_of_file_and_releases_resources() -> None:
    frame_one = object()
    frame_two = object()
    shown_frames: list[object] = []
    wait_delays: list[int] = []
    destroyed_windows: list[bool] = []

    class FakeCapture:
        def __init__(self) -> None:
            self.frames = iter([("ok", frame_one), ("ok", frame_two), ("eof", None)])
            self.released = False

        def read(self) -> tuple[bool, object | None]:
            status, frame = next(self.frames)
            return status == "ok", frame

        def release(self) -> None:
            self.released = True

    capture = FakeCapture()

    def show_frame(_window_name: str, frame: object) -> None:
        shown_frames.append(frame)

    def should_stop(_window_name: str, _delay_ms: int) -> bool:
        wait_delays.append(_delay_ms)
        return False

    def destroy_windows() -> None:
        destroyed_windows.append(True)

    backend = PreviewBackend(
        show_frame=show_frame,
        should_stop=should_stop,
        destroy_windows=destroy_windows,
    )

    run_preview_loop(capture, backend)

    assert shown_frames == [frame_one, frame_two]
    assert wait_delays == [33, 33]
    assert capture.released is True
    assert destroyed_windows == [True]


def test_preview_loop_stops_on_user_quit_and_releases_resources() -> None:
    shown_frames: list[object] = []
    destroyed_windows: list[bool] = []

    class FakeCapture:
        def __init__(self) -> None:
            self.released = False

        def read(self) -> tuple[bool, object]:
            return True, object()

        def release(self) -> None:
            self.released = True

    capture = FakeCapture()
    backend = PreviewBackend(
        show_frame=lambda _window_name, frame: shown_frames.append(frame),
        should_stop=lambda _window_name, _delay_ms: True,
        destroy_windows=lambda: destroyed_windows.append(True),
    )

    run_preview_loop(capture, backend)

    assert len(shown_frames) == 1
    assert capture.released is True
    assert destroyed_windows == [True]


def test_run_preview_opens_first_configured_file_source(tmp_path: Path) -> None:
    config_path = tmp_path / "settings.yaml"
    source_file = tmp_path / "sample.mp4"
    write_config(
        config_path,
        storage=tmp_path / "storage",
        source_uri=source_file.as_uri(),
    )
    opened_paths: list[str] = []
    shown_frames: list[object] = []

    class FakeCapture:
        def isOpened(self) -> bool:  # noqa: N802
            return True

        def read(self) -> tuple[bool, object | None]:
            if shown_frames:
                return False, None
            return True, object()

        def release(self) -> None:
            pass

    def capture_factory(target: str | int) -> FakeCapture:
        assert isinstance(target, str)
        opened_paths.append(target)
        return FakeCapture()

    backend = PreviewBackend(
        show_frame=lambda _window_name, frame: shown_frames.append(frame),
        should_stop=lambda _window_name, _delay_ms: False,
        destroy_windows=lambda: None,
    )

    run_preview(load_settings(config_path), capture_factory=capture_factory, backend=backend)

    assert opened_paths == [str(source_file)]
    assert len(shown_frames) == 1


def test_run_preview_opens_first_configured_device_source(tmp_path: Path) -> None:
    config_path = tmp_path / "settings.yaml"
    write_config(
        config_path,
        storage=tmp_path / "storage",
        source_uri="device:0",
    )
    opened_targets: list[str | int] = []
    shown_frames: list[object] = []

    class FakeCapture:
        def isOpened(self) -> bool:  # noqa: N802
            return True

        def read(self) -> tuple[bool, object | None]:
            if shown_frames:
                return False, None
            return True, object()

        def release(self) -> None:
            pass

    def capture_factory(target: str | int) -> FakeCapture:
        opened_targets.append(target)
        return FakeCapture()

    backend = PreviewBackend(
        show_frame=lambda _window_name, frame: shown_frames.append(frame),
        should_stop=lambda _window_name, _delay_ms: False,
        destroy_windows=lambda: None,
    )

    run_preview(load_settings(config_path), capture_factory=capture_factory, backend=backend)

    assert opened_targets == [0]
    assert len(shown_frames) == 1
