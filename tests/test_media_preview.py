"""Tests for the Cereal media preview boundary."""

from __future__ import annotations

import importlib
from datetime import UTC, datetime
from types import ModuleType
from typing import TYPE_CHECKING

import pytest

from cereal.media.preview import PreviewBackend, run_preview, run_preview_loop
from cereal.settings import load_settings
from tests.helpers import write_config

if TYPE_CHECKING:
    from pathlib import Path

    from cereal.media.recording import FrameWriter, WriterContext


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


def test_preview_loop_writes_displayed_frames_and_releases_writer() -> None:
    frame_one = object()
    frame_two = object()
    shown_frames: list[object] = []
    written_frames: list[object] = []

    class FakeCapture:
        def __init__(self) -> None:
            self.frames = iter([("ok", frame_one), ("ok", frame_two), ("eof", None)])

        def read(self) -> tuple[bool, object | None]:
            status, frame = next(self.frames)
            return status == "ok", frame

        def release(self) -> None:
            pass

    class FakeWriter:
        def __init__(self) -> None:
            self.released = False

        def write(self, frame: object) -> None:
            written_frames.append(frame)

        def release(self) -> None:
            self.released = True

    writer = FakeWriter()
    backend = PreviewBackend(
        show_frame=lambda _window_name, frame: shown_frames.append(frame),
        should_stop=lambda _window_name, _delay_ms: False,
        destroy_windows=lambda: None,
    )

    run_preview_loop(FakeCapture(), backend, frame_writer=writer)

    assert shown_frames == [frame_one, frame_two]
    assert written_frames == [frame_one, frame_two]
    assert writer.released is True


def test_preview_loop_treats_keyboard_interrupt_as_graceful_stop() -> None:
    released: list[str] = []

    class FakeCapture:
        def read(self) -> tuple[bool, object]:
            return True, object()

        def release(self) -> None:
            released.append("capture")

    class FakeWriter:
        def write(self, frame: object) -> None:
            del frame
            released.append("write")

        def release(self) -> None:
            released.append("writer")

    backend = PreviewBackend(
        show_frame=lambda _window_name, _frame: None,
        should_stop=lambda _window_name, _delay_ms: raise_keyboard_interrupt(),
        destroy_windows=lambda: released.append("windows"),
    )

    run_preview_loop(FakeCapture(), backend, frame_writer=FakeWriter())

    assert released == ["write", "capture", "writer", "windows"]


def test_preview_loop_destroys_windows_when_writer_release_fails() -> None:
    released: list[str] = []

    class FakeCapture:
        def read(self) -> tuple[bool, object]:
            return True, object()

        def release(self) -> None:
            released.append("capture")

    class FailingWriter:
        def write(self, frame: object) -> None:
            del frame
            released.append("write")

        def release(self) -> None:
            released.append("writer")
            msg = "recording finalize failed"
            raise RuntimeError(msg)

    backend = PreviewBackend(
        show_frame=lambda _window_name, _frame: None,
        should_stop=lambda _window_name, _delay_ms: True,
        destroy_windows=lambda: released.append("windows"),
    )

    with pytest.raises(RuntimeError, match="recording finalize failed"):
        run_preview_loop(FakeCapture(), backend, frame_writer=FailingWriter())

    assert released == ["write", "capture", "writer", "windows"]


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


def test_run_preview_attaches_writer_when_first_source_write_flag_is_true(tmp_path: Path) -> None:
    config_path = tmp_path / "settings.yaml"
    source_file = tmp_path / "sample.mp4"
    config_path.write_text(
        f"""
storage: {tmp_path / "storage"}
sources:
  - name: camera
    uri: {source_file.as_uri()}
    write: true
""".strip(),
        encoding="utf-8",
    )
    recorded_at = datetime(2026, 5, 23, 1, 2, 3, tzinfo=UTC)
    opened_paths: list[str] = []
    writer_paths: list[Path] = []
    written_frames: list[object] = []

    class FakeCapture:
        def isOpened(self) -> bool:  # noqa: N802
            return True

        def read(self) -> tuple[bool, object | None]:
            if written_frames:
                return False, None
            return True, object()

        def release(self) -> None:
            pass

    class FakeWriter:
        def write(self, frame: object) -> None:
            written_frames.append(frame)

        def release(self) -> None:
            pass

    def capture_factory(target: str | int) -> FakeCapture:
        assert isinstance(target, str)
        opened_paths.append(target)
        return FakeCapture()

    backend = PreviewBackend(
        show_frame=lambda _window_name, _frame: None,
        should_stop=lambda _window_name, _delay_ms: False,
        destroy_windows=lambda: None,
    )

    run_preview(
        load_settings(config_path),
        capture_factory=capture_factory,
        backend=backend,
        writer_factory=lambda artifact_path, _writer_context: (
            writer_paths.append(artifact_path) or FakeWriter()
        ),
        clock=lambda: recorded_at,
    )

    assert opened_paths == [str(source_file)]
    assert writer_paths == [tmp_path / "storage" / "camera" / "2026-05-23" / "1779498123.mp4"]
    assert len(written_frames) == 1


def test_run_preview_ignores_later_source_write_flags(tmp_path: Path) -> None:
    config_path = tmp_path / "settings.yaml"
    first_source = tmp_path / "first.mp4"
    second_source = tmp_path / "second.mp4"
    config_path.write_text(
        f"""
storage: {tmp_path / "storage"}
sources:
  - name: first
    uri: {first_source.as_uri()}
  - name: second
    uri: {second_source.as_uri()}
    write: true
""".strip(),
        encoding="utf-8",
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

    run_preview(
        load_settings(config_path),
        capture_factory=capture_factory,
        backend=backend,
        writer_factory=raise_unexpected_writer,
    )

    assert opened_paths == [str(first_source)]
    assert len(shown_frames) == 1


def raise_unexpected_writer(_artifact_path: Path, _writer_context: WriterContext) -> FrameWriter:
    msg = "writer factory should not be called"
    raise AssertionError(msg)


def raise_keyboard_interrupt() -> bool:
    raise KeyboardInterrupt
