"""Command-line entrypoint for Cereal."""

from __future__ import annotations

import logging
import sys
from argparse import ArgumentParser
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, cast

from cereal.agents import AgentRegistry, AgentToolCatalog, load_agent_definition
from cereal.agents.deepagents_runtime import (
    InvokableAgent,
    compose_orchestrator_agent,
    run_orchestrator_smoke,
)
from cereal.agents.detection_lookup_smoke import run_detection_lookup_tool_smoke
from cereal.agents.orchestrator_delegation_smoke import run_orchestrator_delegation_smoke
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
    agent_name: str | None = None


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
    agent_smoke: Callable[[Settings, str], int] | None = None,
) -> int:
    """Run the Cereal process entrypoint."""
    options = parse_cli_options(argv)
    settings = load_settings(options.config_path)
    if options.command == "detections":
        if options.detection_query is None:
            msg = "detection query options are required"
            raise RuntimeError(msg)
        return query(settings, options.detection_query)
    if options.command == "agent":
        if options.agent_name is None:
            msg = "agent name is required"
            raise RuntimeError(msg)
        smoke = agent_smoke or run_agent_smoke
        return smoke(settings, options.agent_name)

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
    parser.add_argument(
        "--agent",
        dest="agent_name",
        choices=("orchestrator", "detection-lookup", "orchestrator-delegation"),
        help="run a narrow local Agent smoke path",
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
    command = namespace.command or "run"
    if namespace.agent_name is not None:
        command = "agent"
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
        command=command,
        detection_query=detection_query,
        agent_name=namespace.agent_name,
    )


def _parse_datetime(value: str) -> datetime:
    """Parse a CLI ISO datetime, accepting Z for UTC."""
    return datetime.fromisoformat(value)


def run_agent_smoke(settings: Settings, agent_name: str) -> int:
    """Run a local Agent smoke path."""
    if agent_name == "detection-lookup":
        result = run_detection_lookup_tool_smoke(settings.orchestrator)
        sys.stdout.write(f"{result}\n")
        return 0

    if agent_name == "orchestrator-delegation":
        result = run_orchestrator_delegation_smoke(settings.orchestrator)
        sys.stdout.write(f"{result.output}\n")
        return 0

    if agent_name != "orchestrator":
        msg = f"unsupported agent smoke target: {agent_name}"
        raise ValueError(msg)

    orchestrator = load_agent_definition("agents/orchestrator.agent")
    agent = compose_orchestrator_agent(
        orchestrator,
        AgentRegistry(()),
        settings.orchestrator,
        AgentToolCatalog({}),
    )
    result = run_orchestrator_smoke(cast("InvokableAgent", agent))
    sys.stdout.write(f"{result}\n")
    return 0
