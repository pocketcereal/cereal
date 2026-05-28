"""Detection store port and SQLite backend."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Protocol, cast

from cereal.detection.types import BoundingBox, DetectionEvent

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

__all__ = ["DetectionEventQuery", "DetectionStore", "SqliteDetectionStore"]


@dataclass(frozen=True)
class DetectionEventQuery:
    """Structured Detection event query."""

    source_name: str | None = None
    class_name: str | None = None
    observed_time_start: datetime | None = None
    observed_time_end: datetime | None = None
    media_time_start: int | None = None
    media_time_end: int | None = None
    min_confidence: float | None = None
    limit: int | None = None


class DetectionStore(Protocol):
    """Append-only Detection event store."""

    def insert_many(self, events: Sequence[DetectionEvent]) -> list[DetectionEvent]:
        """Append Detection events."""

    def query(self, query: DetectionEventQuery) -> list[DetectionEvent]:
        """Return Detection events matching the query."""

    def close(self) -> None:
        """Release store resources."""


class SqliteDetectionStore:
    """SQLite Detection store backend."""

    def __init__(self, database_path: Path) -> None:
        """Open the database and initialize the Detection schema."""
        database_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(database_path)
        self._initialize_schema()

    def insert_many(self, events: Sequence[DetectionEvent]) -> list[DetectionEvent]:
        """Append Detection events and return the domain values unchanged."""
        if not events:
            return []

        self.connection.executemany(
            """
            INSERT INTO detection_events (
                source_name,
                observed_time_s,
                media_time_ms,
                frame_index,
                frame_width,
                frame_height,
                evidence_uri,
                model_name,
                class_id,
                class_name,
                confidence,
                x1,
                y1,
                x2,
                y2,
                track_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [_event_to_row(event) for event in events],
        )
        self.connection.commit()
        return list(events)

    def query(self, query: DetectionEventQuery) -> list[DetectionEvent]:
        """Return Detection events matching optional structured filters."""
        where_clauses: list[str] = []
        parameters: list[object] = []

        if query.source_name is not None:
            where_clauses.append("source_name = ?")
            parameters.append(query.source_name)
        if query.class_name is not None:
            where_clauses.append("class_name = ?")
            parameters.append(query.class_name)
        if query.observed_time_start is not None:
            where_clauses.append("observed_time_s >= ?")
            parameters.append(_datetime_to_utc_iso(query.observed_time_start))
        if query.observed_time_end is not None:
            where_clauses.append("observed_time_s <= ?")
            parameters.append(_datetime_to_utc_iso(query.observed_time_end))
        if query.media_time_start is not None:
            where_clauses.append("media_time_ms >= ?")
            parameters.append(query.media_time_start)
        if query.media_time_end is not None:
            where_clauses.append("media_time_ms <= ?")
            parameters.append(query.media_time_end)
        if query.min_confidence is not None:
            where_clauses.append("confidence >= ?")
            parameters.append(query.min_confidence)

        sql = "SELECT * FROM detection_events"
        if where_clauses:
            sql = f"{sql} WHERE {' AND '.join(where_clauses)}"
        sql = f"{sql} ORDER BY {_order_by_clause(query)}"
        if query.limit is not None:
            sql = f"{sql} LIMIT ?"
            parameters.append(query.limit)

        rows = self.connection.execute(sql, parameters).fetchall()
        return [_row_to_event(row) for row in rows]

    def close(self) -> None:
        """Close the SQLite connection."""
        self.connection.close()

    def _initialize_schema(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS detection_schema_version (
                version INTEGER PRIMARY KEY CHECK (version = 1)
            );

            INSERT OR IGNORE INTO detection_schema_version (version) VALUES (1);

            CREATE TABLE IF NOT EXISTS detection_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_name TEXT NOT NULL,
                observed_time_s TEXT,
                media_time_ms INTEGER,
                frame_index INTEGER NOT NULL,
                frame_width INTEGER NOT NULL,
                frame_height INTEGER NOT NULL,
                evidence_uri TEXT NOT NULL,
                model_name TEXT NOT NULL,
                class_id INTEGER NOT NULL,
                class_name TEXT NOT NULL,
                confidence REAL NOT NULL,
                x1 REAL NOT NULL,
                y1 REAL NOT NULL,
                x2 REAL NOT NULL,
                y2 REAL NOT NULL,
                track_id TEXT,
                CHECK (observed_time_s IS NOT NULL OR media_time_ms IS NOT NULL)
            );

            CREATE INDEX IF NOT EXISTS idx_detection_events_source_observed_time
                ON detection_events (source_name, observed_time_s);
            CREATE INDEX IF NOT EXISTS idx_detection_events_source_media_time
                ON detection_events (source_name, media_time_ms);
            CREATE INDEX IF NOT EXISTS idx_detection_events_source_class_name
                ON detection_events (source_name, class_name);
            CREATE INDEX IF NOT EXISTS idx_detection_events_source_class_name_observed_time
                ON detection_events (source_name, class_name, observed_time_s);
            CREATE INDEX IF NOT EXISTS idx_detection_events_source_class_name_media_time
                ON detection_events (source_name, class_name, media_time_ms);
            """,
        )
        self.connection.commit()


def _event_to_row(event: DetectionEvent) -> tuple[object, ...]:
    box = event.bounding_box
    return (
        event.source_name,
        _datetime_to_utc_iso(event.observed_time) if event.observed_time is not None else None,
        event.media_time_ms,
        event.frame_index,
        event.frame_width,
        event.frame_height,
        event.evidence_uri,
        event.model_name,
        event.class_id,
        event.class_name,
        event.confidence,
        box.x1,
        box.y1,
        box.x2,
        box.y2,
        event.track_id,
    )


def _row_to_event(row: sqlite3.Row | tuple[object, ...]) -> DetectionEvent:
    values = cast("tuple[Any, ...]", row)
    return DetectionEvent(
        source_name=str(values[1]),
        observed_time=_datetime_from_iso(values[2]),
        media_time_ms=_optional_int(values[3]),
        frame_index=int(values[4]),
        frame_width=int(values[5]),
        frame_height=int(values[6]),
        evidence_uri=str(values[7]),
        model_name=str(values[8]),
        class_id=int(values[9]),
        class_name=str(values[10]),
        confidence=float(values[11]),
        bounding_box=BoundingBox(
            x1=float(values[12]),
            y1=float(values[13]),
            x2=float(values[14]),
            y2=float(values[15]),
        ),
        track_id=None if values[16] is None else str(values[16]),
    )


def _datetime_to_utc_iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC).isoformat()


def _datetime_from_iso(value: object) -> datetime | None:
    if value is None:
        return None

    return datetime.fromisoformat(str(value))


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    return int(cast("Any", value))


def _order_by_clause(query: DetectionEventQuery) -> str:
    if query.observed_time_start is not None or query.observed_time_end is not None:
        return "observed_time_s, frame_index, id"
    if query.media_time_start is not None or query.media_time_end is not None:
        return "media_time_ms, frame_index, id"
    return "source_name, observed_time_s, media_time_ms, frame_index, id"
