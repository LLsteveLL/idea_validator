from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from app.graph.builder import run_analysis
from app.schemas.input import IdeaInput


class DummyStructuredLLM:
    def __init__(self, schema):
        self.schema = schema

    def invoke(self, _prompt: str):
        return self.schema(**build_model_values(self.schema))


def build_model_values(schema: type[BaseModel]) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for name, field in schema.model_fields.items():
        annotation = field.annotation
        if annotation is int:
            values[name] = 60
        elif annotation is str:
            values[name] = f"{name}-value"
        elif isinstance(annotation, type) and issubclass(annotation, BaseModel):
            values[name] = build_model_values(annotation)
        else:
            origin = getattr(annotation, "__origin__", None)
            if origin is list:
                values[name] = [f"{name}-item"]
            else:
                values[name] = f"{name}-value"
    return values


class DummyLLM:
    def with_structured_output(self, schema):
        return DummyStructuredLLM(schema)


def test_run_analysis_with_mocked_llm_search_and_retrieval(monkeypatch):
    from app.graph.nodes import (
        business_agent,
        clarify_idea,
        competitor_agent,
        final_synthesizer,
        market_agent,
        risk_agent,
        validation_planner,
    )
    from app.graph.nodes import retrieve_history

    monkeypatch.setattr(clarify_idea, "get_chat_model", lambda temperature=0: DummyLLM())
    monkeypatch.setattr(market_agent, "get_chat_model", lambda temperature=0.2: DummyLLM())
    monkeypatch.setattr(competitor_agent, "get_chat_model", lambda temperature=0.2: DummyLLM())
    monkeypatch.setattr(business_agent, "get_chat_model", lambda temperature=0.2: DummyLLM())
    monkeypatch.setattr(risk_agent, "get_chat_model", lambda temperature=0.2: DummyLLM())
    monkeypatch.setattr(validation_planner, "get_chat_model", lambda temperature=0.2: DummyLLM())
    monkeypatch.setattr(final_synthesizer, "get_chat_model", lambda temperature=0.2: DummyLLM())

    monkeypatch.setattr(
        market_agent,
        "search_web",
        lambda query: [market_agent.SearchResult(title="market", url="https://example.com", content="market content")],
    )
    monkeypatch.setattr(
        competitor_agent,
        "search_web",
        lambda query: [competitor_agent.SearchResult(title="competitor", url="https://example.com", content="competitor content")],
    )
    monkeypatch.setattr(
        retrieve_history,
        "retrieve_similar_analyses",
        lambda current_input: [
            {
                "analysis_id": 1,
                "similarity": 0.9,
                "idea": current_input["idea"],
                "target_user": current_input["target_user"],
                "problem": current_input["problem"],
                "verdict": "narrow",
                "overall_score": 60,
                "summary": "historical match",
            }
        ],
    )

    payload = IdeaInput(
        idea="AI fitness coach app",
        target_user="busy office workers",
        problem="They do not know how to plan workouts and stay consistent",
        monetization="Monthly subscription",
        resources="Product and AI engineering",
        stage="idea",
        geography="US",
    )
    result = run_analysis(payload)

    assert len(result["market_search_results"]) == 1
    assert len(result["competitor_search_results"]) == 1
    assert len(result["similar_analyses"]) == 1
    assert result["final"]["verdict"] in {"go", "narrow", "no-go"}
    assert "score_breakdown" in result["final"]
    assert "translations" in result["final"]
