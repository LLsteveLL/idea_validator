"""风险分析节点。

识别 idea 最可能失败的点和关键假设。
"""

from pydantic import BaseModel, Field

from app.services.llm import get_chat_model
from app.services.prompt_loader import render_prompt
from app.schemas.state import GraphState


class RiskAnalysis(BaseModel):
    """风险分析的结构化输出。"""

    main_risks: list[str] = Field(description="The biggest reasons this idea may fail.")
    hidden_assumptions: list[str] = Field(description="Unproven assumptions that the idea depends on.")
    execution_risks: list[str] = Field(description="Risks related to building, shipping, or acquiring users.")
    market_risks: list[str] = Field(description="Risks related to demand, competition, or willingness to pay.")
    overall_risk_level: int = Field(ge=0, le=100, description="Higher means riskier.")


def _fallback_risk_analysis(clarified: dict) -> dict:
    """LLM 失败时使用的基础风险分析。"""
    return {
        "main_risks": [
            "Weak differentiation versus existing tools",
            "Unclear willingness to pay",
            "Risk of solving a low-urgency problem",
        ],
        "hidden_assumptions": [
            f"{clarified['target_user']} will change current behavior",
            "A simpler wedge can later expand into a broader product",
        ],
        "execution_risks": [
            "Customer acquisition may be more expensive than expected",
            "Early retention may be weak without a sharp use case",
        ],
        "market_risks": [
            "Demand may be present but too shallow for a strong business",
        ],
        "overall_risk_level": 61,
    }


def risk_agent(state: GraphState) -> dict:
    """输出主要风险、隐藏假设和总体风险等级。"""
    clarified = state["clarified_input"]

    prompt = render_prompt("risk", **clarified)

    try:
        llm = get_chat_model(temperature=0.2)
        structured_llm = llm.with_structured_output(RiskAnalysis)
        risk = structured_llm.invoke(prompt)
        return {"risk": risk.model_dump()}
    except Exception:
        return {"risk": _fallback_risk_analysis(clarified)}
