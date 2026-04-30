"""竞品分析节点。

第一版返回占位性质的竞品和替代方案分析。
"""

from pydantic import BaseModel, Field

from app.core.logging import get_logger
from app.services.llm import get_chat_model
from app.services.prompt_loader import render_prompt
from app.services.tracing import traceable, with_path_debug
from app.services.web_search import SearchResult, SearchUnavailableError, format_search_context, search_web
from app.schemas.state import GraphState

logger = get_logger(__name__)


class CompetitorAnalysis(BaseModel):
    """竞品分析的结构化输出。"""

    direct_competitors: list[str] = Field(description="Likely direct competitors or product categories.")
    indirect_alternatives: list[str] = Field(description="Substitutes users may choose instead.")
    saturation_level: int = Field(ge=0, le=100, description="How crowded the space appears to be.")
    differentiation_ideas: list[str] = Field(description="Ways the product might differentiate.")
    gaps: list[str] = Field(description="Weaknesses or missing pieces in the current positioning.")
    score: int = Field(ge=0, le=100, description="Higher means better competitive room.")


def _fallback_competitor_analysis(clarified: dict) -> dict:
    """LLM 失败时使用的基础竞品分析。"""
    return {
        "direct_competitors": [
            f"Existing apps serving {clarified['target_user']}",
            "AI-first niche startup tools",
        ],
        "indirect_alternatives": [
            "Spreadsheets",
            "Notion",
            "Manual consulting or coaching",
        ],
        "saturation_level": 70,
        "differentiation_ideas": [
            "Narrow the user segment further",
            "Focus on one painful workflow first",
            "Offer a faster validation loop than generic tools",
        ],
        "gaps": [
            "Differentiation is not yet clearly defined",
            "Users may stick with existing low-effort substitutes",
        ],
        "score": 54,
    }


def _build_competitor_query(clarified: dict) -> str:
    """Create a search query oriented around competitor discovery."""
    return (
        f"{clarified['idea']} {clarified['target_user']} {clarified['problem']} "
        f"competitors alternatives pricing {clarified['geography']}"
    )


def _serialize_results(results: list[SearchResult]) -> list[dict]:
    """Convert search results into graph-state-safe dictionaries."""
    return [{"title": item.title, "url": item.url, "content": item.content} for item in results]


@traceable(name="competitor_agent")
def competitor_agent(state: GraphState) -> dict:
    """返回直接竞品、替代方案和差异化建议。"""
    clarified = state["clarified_input"]
    search_results: list[SearchResult] = []
    similar_analyses = state.get("similar_analyses", [])

    try:
        search_results = search_web(_build_competitor_query(clarified))
    except SearchUnavailableError as exc:
        logger.info("Competitor search unavailable: %s", exc)
    except Exception as exc:
        logger.warning("Competitor search failed: %s", exc)

    prompt = render_prompt(
        "competitor",
        search_context=format_search_context(search_results),
        similar_analyses=similar_analyses,
        **clarified,
    )

    try:
        llm = get_chat_model(temperature=0.2)
        structured_llm = llm.with_structured_output(CompetitorAnalysis)
        competitors = structured_llm.invoke(prompt)
        return with_path_debug({
            "competitors": competitors.model_dump(),
            "competitor_search_results": _serialize_results(search_results),
        }, llm_used=True)
    except Exception:
        return with_path_debug({
            "competitors": _fallback_competitor_analysis(clarified),
            "competitor_search_results": _serialize_results(search_results),
        }, llm_used=False)
