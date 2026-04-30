"""商业模式分析节点。

评估 idea 的变现清晰度和执行可行性。
"""

from pydantic import BaseModel, Field

from app.services.llm import get_chat_model
from app.services.prompt_loader import render_prompt
from app.schemas.state import GraphState


class BusinessAnalysis(BaseModel):
    """商业模式分析的结构化输出。"""

    monetization_clarity: str = Field(description="How clear the monetization model appears to be.")
    revenue_potential: int = Field(ge=0, le=100, description="Estimated revenue potential.")
    acquisition_difficulty: int = Field(ge=0, le=100, description="How hard acquiring customers may be.")
    delivery_complexity: int = Field(ge=0, le=100, description="How hard the product or service may be to deliver.")
    notes: list[str] = Field(description="Key observations about the business model.")
    score: int = Field(ge=0, le=100, description="Overall business viability score.")


def _fallback_business_analysis(clarified: dict) -> dict:
    """LLM 失败时使用的基础商业模式分析。"""
    monetization = clarified["monetization"]
    has_monetization = monetization != "Not provided"
    return {
        "monetization_clarity": "high" if has_monetization else "low",
        "revenue_potential": 65 if has_monetization else 45,
        "acquisition_difficulty": 62,
        "delivery_complexity": 55,
        "notes": [
            f"Monetization approach: {monetization}",
            "Execution feasibility depends on distribution advantage and product focus",
        ],
        "score": 64 if has_monetization else 48,
    }


def business_agent(state: GraphState) -> dict:
    """返回商业模式和执行可行性的分析结果。"""
    clarified = state["clarified_input"]

    prompt = render_prompt("business", **clarified)

    try:
        llm = get_chat_model(temperature=0.2)
        structured_llm = llm.with_structured_output(BusinessAnalysis)
        business = structured_llm.invoke(prompt)
        return {"business": business.model_dump()}
    except Exception:
        return {"business": _fallback_business_analysis(clarified)}
