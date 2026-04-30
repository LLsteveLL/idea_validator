"""市场分析节点。

第一版用简单规则模拟市场需求判断。
"""

from pydantic import BaseModel, Field

from app.core.logging import get_logger
from app.services.llm import get_chat_model
from app.services.prompt_loader import render_prompt
from app.services.web_search import SearchResult, SearchUnavailableError, format_search_context, search_web
from app.schemas.state import GraphState

logger = get_logger(__name__)


class MarketAnalysis(BaseModel):
    """市场分析的结构化输出。"""

    demand_summary: str = Field(description="A concise summary of whether demand appears real.")
    target_audience_clarity: str = Field(description="How clearly the target audience is defined.")
    urgency_level: int = Field(ge=0, le=100, description="How urgent or painful the problem seems.")
    market_signals: list[str] = Field(description="Signals that suggest real user demand may exist.")
    concerns: list[str] = Field(description="Reasons to be cautious about the market opportunity.")
    score: int = Field(ge=0, le=100, description="Overall market attractiveness score.")


def _fallback_market_analysis(clarified: dict) -> dict:
    """LLM 失败时使用的基础市场分析。"""
    demand_score = 72 if len(clarified["problem"]) > 20 else 58
    return {
        "demand_summary": (
            f"The problem '{clarified['problem']}' appears understandable for "
            f"{clarified['target_user']} and likely has some real demand."
        ),
        "target_audience_clarity": "medium",
        "urgency_level": 68,
        "market_signals": [
            "Problem statement is concrete enough to evaluate",
            "Target user group is identifiable",
            "Could be tested with landing-page or interview validation",
        ],
        "concerns": [
            "No external market evidence has been collected yet",
            "Demand strength still needs real user validation",
        ],
        "score": demand_score,
    }


def _build_market_query(clarified: dict) -> str:
    """Create a search query oriented around demand and market signals."""
    return (
        f"{clarified['idea']} {clarified['target_user']} {clarified['problem']} "
        f"market demand competitors trends {clarified['geography']}"
    )


def _serialize_results(results: list[SearchResult]) -> list[dict]:
    """Convert search results into graph-state-safe dictionaries."""
    return [{"title": item.title, "url": item.url, "content": item.content} for item in results]


def market_agent(state: GraphState) -> dict:
    """返回一个面向需求判断的市场分析结果。"""
    clarified = state["clarified_input"]
    search_results: list[SearchResult] = []
    similar_analyses = state.get("similar_analyses", [])

    try:
        search_results = search_web(_build_market_query(clarified))
    except SearchUnavailableError as exc:
        logger.info("Market search unavailable: %s", exc)
    except Exception as exc:
        logger.warning("Market search failed: %s", exc)

    prompt = render_prompt(
        "market",
        search_context=format_search_context(search_results),
        similar_analyses=similar_analyses,
        **clarified,
    )

    try:
        llm = get_chat_model(temperature=0.2)
        structured_llm = llm.with_structured_output(MarketAnalysis)
        market = structured_llm.invoke(prompt)
        return {
            "market": market.model_dump(),
            "market_search_results": _serialize_results(search_results),
        }
    except Exception:
        return {
            "market": _fallback_market_analysis(clarified),
            "market_search_results": _serialize_results(search_results),
        }
