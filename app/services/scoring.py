"""Scoring helpers."""

from app.schemas.output import (
    EvidenceItem,
    ReportEvidence,
    ScoreBreakdown,
    ScoreExplanation,
    ScoreExplanationSet,
    SimilarAnalysisEvidence,
)


def compute_score_breakdown(
    market_score: int,
    competitor_score: int,
    business_score: int,
    risk_penalty: int,
) -> ScoreBreakdown:
    """Compute weighted component scores and the final total."""
    market_weighted = round(market_score * 0.35)
    competitor_weighted = round(competitor_score * 0.2)
    business_weighted = round(business_score * 0.3)
    risk_adjusted = 100 - risk_penalty
    risk_weighted = round(risk_adjusted * 0.15)
    overall_score = int(market_weighted + competitor_weighted + business_weighted + risk_weighted)

    return ScoreBreakdown(
        market=market_score,
        competition=competitor_score,
        business=business_score,
        risk=risk_adjusted,
        weighted_market=market_weighted,
        weighted_competition=competitor_weighted,
        weighted_business=business_weighted,
        weighted_risk=risk_weighted,
        overall_score=overall_score,
    )


def derive_verdict(overall_score: int) -> str:
    """Map a total score to a human-readable verdict."""
    if overall_score >= 75:
        return "go"
    if overall_score >= 55:
        return "narrow"
    return "no-go"


def build_score_explanations(state: dict, score_breakdown: ScoreBreakdown) -> ScoreExplanationSet:
    """Build human-readable explanations for each scoring dimension."""
    market = state["market"]
    competitors = state["competitors"]
    business = state["business"]
    risk = state["risk"]

    return ScoreExplanationSet(
        market=ScoreExplanation(
            score=score_breakdown.market,
            weighted_score=score_breakdown.weighted_market,
            rationale=market.get(
                "demand_summary",
                "Market demand could not be deeply evaluated, so this score is conservative.",
            ),
            positive_signals=market.get("market_signals", [])[:3],
            negative_signals=market.get("concerns", [])[:3],
        ),
        competition=ScoreExplanation(
            score=score_breakdown.competition,
            weighted_score=score_breakdown.weighted_competition,
            rationale=(
                "Competition score reflects how much room exists to differentiate "
                "against direct products and indirect substitutes."
            ),
            positive_signals=competitors.get("differentiation_ideas", [])[:3],
            negative_signals=competitors.get("gaps", [])[:3],
        ),
        business=ScoreExplanation(
            score=score_breakdown.business,
            weighted_score=score_breakdown.weighted_business,
            rationale=(
                "Business score reflects monetization clarity, likely revenue potential, "
                "and the expected difficulty of acquiring and serving customers."
            ),
            positive_signals=business.get("notes", [])[:2],
            negative_signals=[
                f"Acquisition difficulty: {business.get('acquisition_difficulty', 'n/a')}",
                f"Delivery complexity: {business.get('delivery_complexity', 'n/a')}",
            ],
        ),
        risk=ScoreExplanation(
            score=score_breakdown.risk,
            weighted_score=score_breakdown.weighted_risk,
            rationale=(
                "Risk score is inverted from the risk penalty: higher means the idea "
                "looks less fragile across market, execution, and willingness-to-pay risks."
            ),
            positive_signals=[
                "Lower overall risk increases this score.",
            ],
            negative_signals=risk.get("main_risks", [])[:3],
        ),
    )


def build_report_evidence(state: dict) -> ReportEvidence:
    """Build compact evidence payloads from search and retrieval state."""
    market_items = [
        EvidenceItem(
            title=item.get("title", ""),
            url=item.get("url"),
            summary=item.get("content", ""),
        )
        for item in state.get("market_search_results", [])[:3]
    ]
    competitor_items = [
        EvidenceItem(
            title=item.get("title", ""),
            url=item.get("url"),
            summary=item.get("content", ""),
        )
        for item in state.get("competitor_search_results", [])[:3]
    ]
    similar_items = [
        SimilarAnalysisEvidence(
            analysis_id=item.get("analysis_id"),
            similarity=item.get("similarity", 0.0),
            idea=item.get("idea", ""),
            verdict=item.get("verdict"),
            overall_score=item.get("overall_score"),
            summary=item.get("summary", ""),
        )
        for item in state.get("similar_analyses", [])[:3]
    ]

    return ReportEvidence(
        market_search=market_items,
        competitor_search=competitor_items,
        similar_analyses=similar_items,
    )
