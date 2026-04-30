"""最终汇总节点。

把前面所有节点的结果整合成最终对外返回的报告结构。
"""

from pydantic import BaseModel, Field

from app.services.llm import get_chat_model
from app.services.prompt_loader import render_prompt
from app.services.scoring import compute_score_breakdown, derive_verdict
from app.schemas.output import FinalReport
from app.schemas.state import GraphState


class FinalNarrative(BaseModel):
    """最终结论中的 LLM 叙述部分。"""

    summary: str = Field(description="A concise final summary of the idea's viability.")
    opportunities: list[str] = Field(description="The strongest reasons the idea could work.")
    risks: list[str] = Field(description="The strongest reasons the idea could fail.")
    key_assumptions: list[str] = Field(description="The assumptions that must be validated first.")
    next_steps: list[str] = Field(description="Concrete immediate actions to validate the idea.")


def _fallback_final_report(state: GraphState, verdict: str, score_breakdown) -> dict:
    """LLM 失败时使用的最终报告拼装逻辑。"""
    report = FinalReport(
        verdict=verdict,
        overall_score=score_breakdown.overall_score,
        score_breakdown=score_breakdown,
        summary=(
            "This idea has some visible potential, but the current version still "
            "needs sharper positioning and real user validation before serious investment."
        ),
        opportunities=state["market"]["market_signals"] + state["competitors"]["differentiation_ideas"][:1],
        risks=state["risk"]["main_risks"],
        key_assumptions=state["validation"]["key_assumptions_to_test"],
        next_steps=state["validation"]["experiments"],
    )
    return report.model_dump()


def final_synthesizer(state: GraphState) -> dict:
    """汇总中间分析结果，并生成 `FinalReport`。"""
    market_score = state["market"]["score"]
    competitor_score = state["competitors"]["score"]
    business_score = state["business"]["score"]
    risk_penalty = state["risk"]["overall_risk_level"]

    score_breakdown = compute_score_breakdown(
        market_score=market_score,
        competitor_score=competitor_score,
        business_score=business_score,
        risk_penalty=risk_penalty,
    )
    verdict = derive_verdict(score_breakdown.overall_score)

    prompt = render_prompt(
        "final",
        verdict=verdict,
        overall_score=score_breakdown.overall_score,
        market=state["market"],
        competitors=state["competitors"],
        business=state["business"],
        risk=state["risk"],
        validation=state["validation"],
        similar_analyses=state.get("similar_analyses", []),
    )

    try:
        llm = get_chat_model(temperature=0.2)
        structured_llm = llm.with_structured_output(FinalNarrative)
        narrative = structured_llm.invoke(prompt)
        report = FinalReport(
            verdict=verdict,
            overall_score=score_breakdown.overall_score,
            score_breakdown=score_breakdown,
            summary=narrative.summary,
            opportunities=narrative.opportunities,
            risks=narrative.risks,
            key_assumptions=narrative.key_assumptions,
            next_steps=narrative.next_steps,
        )
        return {"final": report.model_dump()}
    except Exception:
        return {"final": _fallback_final_report(state, verdict, score_breakdown)}
