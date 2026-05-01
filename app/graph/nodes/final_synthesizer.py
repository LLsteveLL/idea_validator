"""最终汇总节点。

把前面所有节点的结果整合成最终对外返回的报告结构。
"""

from pydantic import BaseModel, Field

from app.services.llm import get_chat_model
from app.services.prompt_loader import render_prompt
from app.services.scoring import (
    build_report_evidence,
    build_score_explanations,
    compute_score_breakdown,
    derive_verdict,
)
from app.services.tracing import traceable, with_path_debug
from app.schemas.output import FinalReport
from app.schemas.state import GraphState


class FinalLocalizedScoreExplanationText(BaseModel):
    """单个维度的本地化文案。"""

    rationale: str = Field(description="Localized explanation for why this score was assigned.")
    positive_signals: list[str] = Field(description="Localized positive signals behind this score.")
    negative_signals: list[str] = Field(description="Localized negative signals behind this score.")


class FinalLocalizedScoreExplanationTextSet(BaseModel):
    """四个维度的本地化评分文案。"""

    market: FinalLocalizedScoreExplanationText
    competition: FinalLocalizedScoreExplanationText
    business: FinalLocalizedScoreExplanationText
    risk: FinalLocalizedScoreExplanationText


class FinalLocalizedNarrative(BaseModel):
    """单个语言版本的总结内容。"""

    summary: str = Field(description="Localized final summary.")
    opportunities: list[str] = Field(description="Localized list of strongest opportunities.")
    risks: list[str] = Field(description="Localized list of strongest risks.")
    key_assumptions: list[str] = Field(description="Localized validation-oriented assumptions.")
    next_steps: list[str] = Field(description="Localized immediate next steps.")
    score_explanations: FinalLocalizedScoreExplanationTextSet


class FinalNarrative(BaseModel):
    """最终结论中的双语 LLM 叙述部分。"""

    en: FinalLocalizedNarrative
    zh: FinalLocalizedNarrative


def _build_fallback_translations(report: FinalReport) -> dict:
    """Build a bilingual fallback when the richer LLM path is unavailable."""
    explanation_texts = {
        "market": {
            "rationale": report.score_explanations.market.rationale,
            "positive_signals": report.score_explanations.market.positive_signals,
            "negative_signals": report.score_explanations.market.negative_signals,
        },
        "competition": {
            "rationale": report.score_explanations.competition.rationale,
            "positive_signals": report.score_explanations.competition.positive_signals,
            "negative_signals": report.score_explanations.competition.negative_signals,
        },
        "business": {
            "rationale": report.score_explanations.business.rationale,
            "positive_signals": report.score_explanations.business.positive_signals,
            "negative_signals": report.score_explanations.business.negative_signals,
        },
        "risk": {
            "rationale": report.score_explanations.risk.rationale,
            "positive_signals": report.score_explanations.risk.positive_signals,
            "negative_signals": report.score_explanations.risk.negative_signals,
        },
    }
    english = {
        "summary": report.summary,
        "opportunities": report.opportunities,
        "risks": report.risks,
        "key_assumptions": report.key_assumptions,
        "next_steps": report.next_steps,
        "score_explanations": explanation_texts,
    }
    chinese = {
        "summary": report.summary,
        "opportunities": report.opportunities,
        "risks": report.risks,
        "key_assumptions": report.key_assumptions,
        "next_steps": report.next_steps,
        "score_explanations": explanation_texts,
    }
    return {"en": english, "zh": chinese}


def _fallback_final_report(state: GraphState, verdict: str, score_breakdown) -> dict:
    """LLM 失败时使用的最终报告拼装逻辑。"""
    score_explanations = build_score_explanations(state, score_breakdown)
    evidence = build_report_evidence(state)
    report = FinalReport(
        verdict=verdict,
        overall_score=score_breakdown.overall_score,
        score_breakdown=score_breakdown,
        score_explanations=score_explanations,
        translations=_build_fallback_translations(
            FinalReport(
                verdict=verdict,
                overall_score=score_breakdown.overall_score,
                score_breakdown=score_breakdown,
                score_explanations=score_explanations,
                summary=(
                    f"This run could only produce a conservative final narrative for '{state['clarified_input']['idea']}' "
                    "because the richer synthesis path was unavailable. The structure below should still help you decide what to validate next."
                ),
                opportunities=state["market"]["market_signals"] + state["competitors"]["differentiation_ideas"][:1],
                risks=state["risk"]["main_risks"],
                key_assumptions=state["validation"]["key_assumptions_to_test"],
                next_steps=state["validation"]["experiments"],
                evidence=evidence,
            )
        ),
        summary=(
            f"This run could only produce a conservative final narrative for '{state['clarified_input']['idea']}' "
            "because the richer synthesis path was unavailable. The structure below should still help you decide what to validate next."
        ),
        opportunities=state["market"]["market_signals"] + state["competitors"]["differentiation_ideas"][:1],
        risks=state["risk"]["main_risks"],
        key_assumptions=state["validation"]["key_assumptions_to_test"],
        next_steps=state["validation"]["experiments"],
        evidence=evidence,
    )
    return report.model_dump()


@traceable(name="final_synthesizer")
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
    score_explanations = build_score_explanations(state, score_breakdown)
    evidence = build_report_evidence(state)
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
        score_explanations=score_explanations.model_dump(),
    )

    try:
        llm = get_chat_model(temperature=0.2)
        structured_llm = llm.with_structured_output(FinalNarrative)
        narrative = structured_llm.invoke(prompt)
        report = FinalReport(
            verdict=verdict,
            overall_score=score_breakdown.overall_score,
            score_breakdown=score_breakdown,
            score_explanations=score_explanations,
            translations=narrative.model_dump(),
            summary=narrative.en.summary,
            opportunities=narrative.en.opportunities,
            risks=narrative.en.risks,
            key_assumptions=narrative.en.key_assumptions,
            next_steps=narrative.en.next_steps,
            evidence=evidence,
        )
        return with_path_debug({"final": report.model_dump()}, llm_used=True)
    except Exception:
        return with_path_debug({"final": _fallback_final_report(state, verdict, score_breakdown)}, llm_used=False)
