"""Command-line entrypoint for Cereal."""

from __future__ import annotations

import logging
from argparse import ArgumentParser
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from cereal.detection.query import DetectionQueryOptions, run_detection_query
from cereal.detection.runtime import run_detection_preview
from cereal.settings import DEFAULT_CONFIG_PATH, Settings, load_settings

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CliOptions:
    """Runtime options selected from CLI arguments."""

    config_path: Path
    preview_enabled: bool = True
    overlays_enabled: bool = False
    command: str = "run"
    detection_query: DetectionQueryOptions | None = None


def run(
    settings: Settings,
    *,
    preview_enabled: bool = True,
    overlays_enabled: bool = False,
    preview: Callable[..., None] = run_detection_preview,
) -> int:
    """Run the Cereal CLI."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    logger.info(
        "starting Cereal config_storage=%s preview=%s overlays=%s",
        settings.storage,
        "on" if preview_enabled else "off",
        "on" if overlays_enabled else "off",
    )
    preview(
        settings,
        preview_enabled=preview_enabled,
        enable_overlays=overlays_enabled,
    )
    return 0


def main(
    argv: Sequence[str] | None = None,
    *,
    preview: Callable[..., None] = run_detection_preview,
    query: Callable[[Settings, DetectionQueryOptions], int] = run_detection_query,
) -> int:
    """Run the Cereal process entrypoint."""
    options = parse_cli_options(argv)
    settings = load_settings(options.config_path)
    if options.command == "detections":
        if options.detection_query is None:
            msg = "detection query options are required"
            raise RuntimeError(msg)
        return query(settings, options.detection_query)

    return run(
        settings,
        preview_enabled=options.preview_enabled,
        overlays_enabled=options.overlays_enabled,
        preview=preview,
    )


def parse_cli_options(args: Sequence[str] | None = None) -> CliOptions:
    """Parse Cereal CLI options."""
    parser = ArgumentParser(prog="cereal")
    parser.add_argument("--config", dest="config_path", type=Path, default=DEFAULT_CONFIG_PATH)
    preview_group = parser.add_mutually_exclusive_group()
    preview_group.add_argument("--preview", dest="preview_enabled", action="store_true")
    preview_group.add_argument("--no-preview", dest="preview_enabled", action="store_false")
    parser.add_argument(
        "--overlays",
        dest="overlays_enabled",
        action="store_true",
        help="draw sampled Detection overlays in the Preview window",
    )
    subparsers = parser.add_subparsers(dest="command")
    detections_parser = subparsers.add_parser(
        "detections",
        help="query stored Detection events",
    )
    detections_parser.add_argument("--config", dest="detections_config_path", type=Path)
    detections_parser.add_argument("--source", dest="source_name")
    detections_parser.add_argument("--class", "--class-name", dest="class_name")
    detections_parser.add_argument("--min-confidence", dest="min_confidence", type=float)
    detections_parser.add_argument("--observed-start", type=_parse_datetime)
    detections_parser.add_argument("--observed-end", type=_parse_datetime)
    detections_parser.add_argument("--media-start-ms", dest="media_time_start", type=int)
    detections_parser.add_argument("--media-end-ms", dest="media_time_end", type=int)
    detections_parser.add_argument("--limit", type=int, default=20)
    parser.set_defaults(preview_enabled=True)
    namespace = parser.parse_args(args)
    detection_query = None
    if namespace.command == "detections":
        detection_query = DetectionQueryOptions(
            source_name=namespace.source_name,
            class_name=namespace.class_name,
            observed_time_start=namespace.observed_start,
            observed_time_end=namespace.observed_end,
            media_time_start=namespace.media_time_start,
            media_time_end=namespace.media_time_end,
            min_confidence=namespace.min_confidence,
            limit=namespace.limit,
        )

    return CliOptions(
        config_path=getattr(namespace, "detections_config_path", None) or namespace.config_path,
        preview_enabled=namespace.preview_enabled,
        overlays_enabled=namespace.overlays_enabled,
        command=namespace.command or "run",
        detection_query=detection_query,
    )


def _parse_datetime(value: str) -> datetime:
    """Parse a CLI ISO datetime, accepting Z for UTC."""
    return datetime.fromisoformat(value)
