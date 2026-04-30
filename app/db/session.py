"""SQLite persistence helpers."""

import json
import sqlite3
from pathlib import Path
from typing import Any

from app.core.settings import settings


def _resolve_sqlite_path(database_url: str) -> Path:
    """Convert a sqlite URL into a filesystem path."""
    if not database_url.startswith("sqlite:///"):
        raise ValueError("Only sqlite:/// URLs are supported in the current MVP.")
    raw_path = database_url.removeprefix("sqlite:///")
    return Path(raw_path).resolve()


def get_connection() -> sqlite3.Connection:
    """Open a SQLite connection for the configured database."""
    db_path = _resolve_sqlite_path(settings.database_url)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    """Create required tables if they do not already exist."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                idea_input TEXT NOT NULL,
                graph_state TEXT NOT NULL,
                final_report TEXT NOT NULL
            )
            """
        )
        connection.commit()


def save_analysis(idea_input: dict[str, Any], graph_state: dict[str, Any], final_report: dict[str, Any]) -> int:
    """Persist an analysis run and return its record ID."""
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO analyses (idea_input, graph_state, final_report)
            VALUES (?, ?, ?)
            """,
            (
                json.dumps(idea_input, ensure_ascii=False),
                json.dumps(graph_state, ensure_ascii=False),
                json.dumps(final_report, ensure_ascii=False),
            ),
        )
        connection.commit()
        return int(cursor.lastrowid)


def load_recent_analyses(limit: int = 25) -> list[dict[str, Any]]:
    """Load recent persisted analyses for retrieval."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, created_at, idea_input, final_report
            FROM analyses
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    results: list[dict[str, Any]] = []
    for row in rows:
        results.append(
            {
                "id": row["id"],
                "created_at": row["created_at"],
                "idea_input": json.loads(row["idea_input"]),
                "final_report": json.loads(row["final_report"]),
            }
        )
    return results


def load_analysis_by_id(analysis_id: int) -> dict[str, Any] | None:
    """Load a single persisted analysis by ID."""
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, created_at, idea_input, final_report
            FROM analyses
            WHERE id = ?
            """,
            (analysis_id,),
        ).fetchone()

    if row is None:
        return None

    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "idea_input": json.loads(row["idea_input"]),
        "final_report": json.loads(row["final_report"]),
    }
