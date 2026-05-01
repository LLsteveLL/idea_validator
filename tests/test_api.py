from __future__ import annotations

from fastapi.testclient import TestClient

from app.db.session import init_db
from app.main import app
from app.schemas.output import (
    EvidenceItem,
    FinalReport,
    LocalizedNarrative,
    LocalizedScoreExplanationText,
    LocalizedScoreExplanationTextSet,
    ReportEvidence,
    ReportTranslations,
    ScoreBreakdown,
    ScoreExplanation,
    ScoreExplanationSet,
    SimilarAnalysisEvidence,
)


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
        score_explanations=ScoreExplanationSet(
            market=ScoreExplanation(
                score=70,
                weighted_score=24,
                rationale="Clear problem statement.",
                positive_signals=["Clear target user"],
                negative_signals=["Needs stronger evidence"],
            ),
            competition=ScoreExplanation(
                score=50,
                weighted_score=10,
                rationale="Competition looks moderate.",
                positive_signals=["Some differentiation exists"],
                negative_signals=["Crowded category"],
            ),
            business=ScoreExplanation(
                score=60,
                weighted_score=18,
                rationale="Monetization is understandable.",
                positive_signals=["Subscription model"],
                negative_signals=["Unknown acquisition cost"],
            ),
            risk=ScoreExplanation(
                score=40,
                weighted_score=6,
                rationale="Execution still looks fragile.",
                positive_signals=["Can be validated quickly"],
                negative_signals=["Users may not pay"],
            ),
        ),
        translations=ReportTranslations(
            en=LocalizedNarrative(
                summary="Useful but needs validation.",
                opportunities=["Clear target user"],
                risks=["Crowded category"],
                key_assumptions=["Users will pay"],
                next_steps=["Interview users"],
                score_explanations=LocalizedScoreExplanationTextSet(
                    market=LocalizedScoreExplanationText(
                        rationale="Clear problem statement.",
                        positive_signals=["Clear target user"],
                        negative_signals=["Needs stronger evidence"],
                    ),
                    competition=LocalizedScoreExplanationText(
                        rationale="Competition looks moderate.",
                        positive_signals=["Some differentiation exists"],
                        negative_signals=["Crowded category"],
                    ),
                    business=LocalizedScoreExplanationText(
                        rationale="Monetization is understandable.",
                        positive_signals=["Subscription model"],
                        negative_signals=["Unknown acquisition cost"],
                    ),
                    risk=LocalizedScoreExplanationText(
                        rationale="Execution still looks fragile.",
                        positive_signals=["Can be validated quickly"],
                        negative_signals=["Users may not pay"],
                    ),
                ),
            ),
            zh=LocalizedNarrative(
                summary="这个方向有用，但还需要验证。",
                opportunities=["目标用户清晰"],
                risks=["赛道比较拥挤"],
                key_assumptions=["用户愿意付费"],
                next_steps=["先访谈用户"],
                score_explanations=LocalizedScoreExplanationTextSet(
                    market=LocalizedScoreExplanationText(
                        rationale="问题定义比较清楚。",
                        positive_signals=["目标用户明确"],
                        negative_signals=["还缺更强证据"],
                    ),
                    competition=LocalizedScoreExplanationText(
                        rationale="竞争程度中等。",
                        positive_signals=["还有一些差异化空间"],
                        negative_signals=["赛道拥挤"],
                    ),
                    business=LocalizedScoreExplanationText(
                        rationale="变现方式能说得通。",
                        positive_signals=["订阅模型清晰"],
                        negative_signals=["获客成本未知"],
                    ),
                    risk=LocalizedScoreExplanationText(
                        rationale="执行仍然比较脆弱。",
                        positive_signals=["可以快速验证"],
                        negative_signals=["用户可能不愿付费"],
                    ),
                ),
            ),
        ),
        summary="Useful but needs validation.",
        opportunities=["Clear target user"],
        risks=["Crowded category"],
        key_assumptions=["Users will pay"],
        next_steps=["Interview users"],
        evidence=ReportEvidence(
            market_search=[
                EvidenceItem(title="Market result", url="https://example.com/market", summary="Market context"),
            ],
            competitor_search=[
                EvidenceItem(title="Competitor result", url="https://example.com/competitor", summary="Competitor context"),
            ],
            similar_analyses=[
                SimilarAnalysisEvidence(
                    analysis_id=1,
                    similarity=0.9,
                    idea="AI fitness coach app",
                    verdict="narrow",
                    overall_score=61,
                    summary="Similar historical run",
                )
            ],
        ),
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
