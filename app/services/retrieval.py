"""Retrieval helpers for similar historical analyses."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any

from app.core.logging import get_logger
from app.core.settings import settings
from app.db.session import load_recent_analyses

logger = get_logger(__name__)

TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9]+")


def _tokenize(text: str) -> Counter[str]:
    """Tokenize text into lowercase alphanumeric terms."""
    return Counter(TOKEN_PATTERN.findall(text.lower()))


def _cosine_like_similarity(left: Counter[str], right: Counter[str]) -> float:
    """Compute a lightweight token-overlap similarity score."""
    if not left or not right:
        return 0.0

    intersection = set(left) & set(right)
    numerator = sum(left[token] * right[token] for token in intersection)
    left_norm = sum(value * value for value in left.values()) ** 0.5
    right_norm = sum(value * value for value in right.values()) ** 0.5
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)


def _build_document_text(idea_input: dict[str, Any]) -> str:
    """Flatten the key input fields into a retrieval document."""
    parts = [
        idea_input.get("idea", ""),
        idea_input.get("target_user", ""),
        idea_input.get("problem", ""),
        idea_input.get("monetization", ""),
        idea_input.get("resources", ""),
        idea_input.get("stage", ""),
        idea_input.get("geography", ""),
        idea_input.get("notes", ""),
    ]
    return " ".join(part for part in parts if part).strip()


def retrieve_similar_analyses(current_input: dict[str, Any]) -> list[dict[str, Any]]:
    """Retrieve similar historical analyses from SQLite."""
    current_doc = _build_document_text(current_input)
    current_tokens = _tokenize(current_doc)
    if not current_tokens:
        return []

    candidates = load_recent_analyses(limit=25)
    scored_results: list[dict[str, Any]] = []

    for candidate in candidates:
        candidate_input = candidate.get("idea_input", {})
        candidate_doc = _build_document_text(candidate_input)
        similarity = _cosine_like_similarity(current_tokens, _tokenize(candidate_doc))
        if similarity <= 0:
            continue

        candidate_report = candidate.get("final_report", {})
        scored_results.append(
            {
                "analysis_id": candidate.get("id"),
                "similarity": round(similarity, 4),
                "idea": candidate_input.get("idea", ""),
                "target_user": candidate_input.get("target_user", ""),
                "problem": candidate_input.get("problem", ""),
                "verdict": candidate_report.get("verdict"),
                "overall_score": candidate_report.get("overall_score"),
                "summary": candidate_report.get("summary", ""),
            }
        )

    scored_results.sort(key=lambda item: item["similarity"], reverse=True)
    return scored_results[: settings.retrieval_results_limit]
