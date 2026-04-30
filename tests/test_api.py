from __future__ import annotations

from fastapi.testclient import TestClient

from app.db.session import init_db
from app.main import app
from app.schemas.output import FinalReport, ScoreBreakdown


def test_health_endpoint(temp_db_settings):
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_persists_and_history_endpoints_work(temp_db_settings, monkeypatch):
    from app.api import routes

    report = FinalReport(
        verdict="narrow",
        overall_score=61,
        score_breakdown=ScoreBreakdown(
            market=70,
            competition=50,
            business=60,
            risk=40,
            weighted_market=24,
            weighted_competition=10,
            weighted_business=18,
            weighted_risk=6,
            overall_score=61,
        ),
        summary="Useful but needs validation.",
        opportunities=["Clear target user"],
        risks=["Crowded category"],
        key_assumptions=["Users will pay"],
        next_steps=["Interview users"],
        analysis_id=None,
    )

    def fake_analyze_with_state(_payload):
        return report, {"market": {"score": 70}, "competitors": {"score": 50}}

    monkeypatch.setattr(routes, "analyze_idea_with_state", fake_analyze_with_state)

    init_db()
    client = TestClient(app)
    payload = {
        "idea": "AI fitness coach app",
        "target_user": "busy office workers",
        "problem": "They do not know how to plan workouts and stay consistent",
        "monetization": "Monthly subscription",
        "resources": "Product and AI engineering",
        "stage": "idea",
    }

    analyze_response = client.post("/analyze", json=payload)
    assert analyze_response.status_code == 200
    analyze_body = analyze_response.json()
    assert analyze_body["analysis_id"] == 1

    list_response = client.get("/analyses")
    assert list_response.status_code == 200
    list_body = list_response.json()
    assert len(list_body) == 1
    assert list_body[0]["idea"] == "AI fitness coach app"

    detail_response = client.get("/analyses/1")
    assert detail_response.status_code == 200
    detail_body = detail_response.json()
    assert detail_body["idea_input"]["target_user"] == "busy office workers"
    assert detail_body["final_report"]["verdict"] == "narrow"


def test_get_analysis_returns_404_for_missing_record(temp_db_settings):
    init_db()
    client = TestClient(app)
    response = client.get("/analyses/999")
    assert response.status_code == 404
