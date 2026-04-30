"""Tracing helpers for LangSmith and local debug metadata."""

from langsmith import traceable


def with_path_debug(payload: dict, llm_used: bool) -> dict:
    """Attach lightweight debug metadata to a node payload."""
    payload["debug"] = {
        "path": "llm" if llm_used else "fallback",
    }
    return payload


__all__ = ["traceable", "with_path_debug"]
