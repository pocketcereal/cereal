"""Tests for media source handling."""

from __future__ import annotations

from pathlib import Path

import pytest

from cereal.media.adapters import SourceAdapterRegistry
from cereal.media.device_adapter import DeviceSourceAdapter
from cereal.media.file_adapter import FileSourceAdapter
from cereal.media.registry import default_source_adapter_registry
from cereal.media.sources import first_configured_source, open_first_configured_source
from cereal.media.uris import device_uri_index, file_uri_path, source_uri_scheme
from cereal.settings import SourceSettings, load_settings
from tests.helpers import write_config


class FakeCapture:
    def __init__(self, *, opened: bool = True) -> None:
        self.opened = opened

    def isOpened(self) -> bool:  # noqa: N802
        return self.opened

    def read(self) -> tuple[bool, object | None]:
        return False, None

    def release(self) -> None:
        pass


def test_first_configured_source_selects_first_settings_source(tmp_path: Path) -> None:
    config_path = tmp_path / "settings.yaml"
    first_file = tmp_path / "first.mp4"
    second_file = tmp_path / "second.mp4"
    write_config(
        config_path,
        storage=tmp_path / "storage",
        sources=(("first", first_file.as_uri()), ("second", second_file.as_uri())),
    )

    settings = load_settings(config_path)

    assert first_configured_source(settings).name == "first"


def test_file_uri_path_converts_file_source_uri_to_local_path(tmp_path: Path) -> None:
    source_file = tmp_path / "sample video.mp4"

    assert file_uri_path(source_file.as_uri()) == source_file


def test_file_uri_path_accepts_relative_file_uri() -> None:
    assert file_uri_path("file:data/example.mp4") == Path("data/example.mp4")


def test_device_uri_index_converts_device_source_uri_to_numeric_index() -> None:
    assert device_uri_index("device:0") == 0


def test_source_uri_scheme_returns_source_adapter_lookup_key() -> None:
    assert source_uri_scheme("device:0") == "device"


def test_source_adapter_registry_selects_adapter_by_source_uri_scheme(tmp_path: Path) -> None:
    class FakeAdapter:
        def open(self, source: SourceSettings) -> FakeCapture:
            del source
            return FakeCapture()

    adapter = FakeAdapter()
    registry = SourceAdapterRegistry({"file": adapter})
    source = SourceSettings(name="sample", uri=(tmp_path / "sample.mp4").as_uri())

    assert registry.adapter_for(source) is adapter


def test_default_source_adapter_registry_opens_file_and_device_sources(tmp_path: Path) -> None:
    opened_targets: list[str | int] = []

    def capture_factory(target: str | int) -> FakeCapture:
        opened_targets.append(target)
        return FakeCapture()

    registry = default_source_adapter_registry(capture_factory)
    file_source = SourceSettings(name="sample", uri=(tmp_path / "sample.mp4").as_uri())
    device_source = SourceSettings(name="camera", uri="device:0")

    registry.adapter_for(file_source).open(file_source)
    registry.adapter_for(device_source).open(device_source)

    assert opened_targets == [str(tmp_path / "sample.mp4"), 0]


def test_file_source_adapter_opens_file_uri_with_local_path(tmp_path: Path) -> None:
    opened_paths: list[str] = []
    capture = FakeCapture()

    def capture_factory(path: str) -> FakeCapture:
        opened_paths.append(path)
        return capture

    source_file = tmp_path / "sample.mp4"
    source = SourceSettings(name="sample", uri=source_file.as_uri())
    adapter = FileSourceAdapter(capture_factory)

    assert adapter.open(source) is capture
    assert opened_paths == [str(source_file)]


def test_device_source_adapter_opens_device_uri_with_numeric_index() -> None:
    opened_indexes: list[int] = []
    capture = FakeCapture()

    def capture_factory(index: int) -> FakeCapture:
        opened_indexes.append(index)
        return capture

    source = SourceSettings(name="camera", uri="device:0")
    adapter = DeviceSourceAdapter(capture_factory)

    assert adapter.open(source) is capture
    assert opened_indexes == [0]


def test_file_source_adapter_raises_when_capture_does_not_open(tmp_path: Path) -> None:
    def capture_factory(_path: str) -> FakeCapture:
        return FakeCapture(opened=False)

    source_file = tmp_path / "missing.mp4"
    source = SourceSettings(name="sample", uri=source_file.as_uri())
    adapter = FileSourceAdapter(capture_factory)

    with pytest.raises(RuntimeError, match=str(source_file)):
        adapter.open(source)


def test_open_first_configured_source_uses_first_source_adapter(tmp_path: Path) -> None:
    config_path = tmp_path / "settings.yaml"
    first_file = tmp_path / "first.mp4"
    second_file = tmp_path / "second.mp4"
    write_config(
        config_path,
        storage=tmp_path / "storage",
        sources=(("first", first_file.as_uri()), ("second", second_file.as_uri())),
    )
    capture = FakeCapture()
    opened_source_names: list[str] = []

    class FakeAdapter:
        def open(self, source: SourceSettings) -> FakeCapture:
            opened_source_names.append(source.name)
            return capture

    settings = load_settings(config_path)
    registry = SourceAdapterRegistry({"file": FakeAdapter()})

    assert open_first_configured_source(settings, registry) is capture
    assert opened_source_names == ["first"]
