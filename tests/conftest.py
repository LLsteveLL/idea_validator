from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture
def temp_db_settings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_url = f"sqlite:///{tmp_path / 'test_idea_validator.db'}"
    fake_settings = SimpleNamespace(
        database_url=db_url,
        save_analysis_results=True,
        log_level="INFO",
        app_name="Idea Validator API",
        app_version="0.1.0",
        openai_api_key="test-key",
        openai_model="gpt-4o-mini",
        openai_temperature=0.2,
        request_timeout_seconds=30,
        search_provider="tavily",
        tavily_api_key="test-tavily",
        search_results_limit=5,
        retrieval_results_limit=3,
    )

    monkeypatch.setattr("app.db.session.settings", fake_settings)
    monkeypatch.setattr("app.api.routes.settings", fake_settings)
    monkeypatch.setattr("app.main.settings", fake_settings)
    monkeypatch.setattr("app.core.logging.settings", fake_settings)
    monkeypatch.setattr("app.core.settings.settings", fake_settings)
    return fake_settings
