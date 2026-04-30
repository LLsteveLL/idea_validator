"""Scoring helpers."""

from app.schemas.output import ScoreBreakdown


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
