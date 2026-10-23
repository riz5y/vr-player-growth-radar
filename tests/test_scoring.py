"""
tests/test_scoring.py
Unit tests for the Opportunity Prioritization mathematical formula and scoring calculations.
"""

from src.scoring import calculate_opportunity_score, derive_opportunities_from_reviews
from src.database import DEFAULT_WEIGHTS
import pandas as pd


def test_scoring_formula_calculation():
    """
    Validates exact mathematical calculation:
    Score = [ (w_F * F + w_S * S + w_A * A + w_R * R + w_ES * ES) / (w_E * E) ] * C
    """
    weights = {
        "weight_frequency": 1.0,
        "weight_severity": 2.0,
        "weight_affected_users": 1.0,
        "weight_strategic_relevance": 2.0,
        "weight_evidence_strength": 1.0,
        "weight_effort": 1.0,
    }
    
    # F=4, S=5, A=3, R=4, ES=4, E=2, C=1.0
    # Numerator = (1*4) + (2*5) + (1*3) + (2*4) + (1*4) = 4 + 10 + 3 + 8 + 4 = 29
    # Denominator = (1 * 2) = 2
    # Score = (29 / 2) * 1.0 = 14.50
    result = calculate_opportunity_score(
        frequency=4,
        severity=5,
        affected_users=3,
        strategic_relevance=4,
        evidence_strength=4,
        implementation_effort=2,
        confidence_multiplier=1.0,
        weights=weights,
    )

    assert result["raw_score"] == 14.50
    assert result["numerator"] == 29.0
    assert result["denominator"] == 2.0
    assert 0.0 <= result["normalized_score_100"] <= 100.0


def test_scoring_boundary_and_clamping():
    """Ensures input clamping prevents division by zero or negative scores."""
    result = calculate_opportunity_score(
        frequency=-5,
        severity=99,
        affected_users=0,
        strategic_relevance=10,
        evidence_strength=1,
        implementation_effort=0,
        confidence_multiplier=0.1,
    )
    assert result["raw_score"] > 0
    assert result["denominator"] > 0
    assert 0.0 <= result["normalized_score_100"] <= 100.0


def test_derive_opportunities_from_reviews():
    """Verifies that review clusters generate prioritized opportunity items."""
    df = pd.DataFrame([
        {"review_id": "r1", "rating": 1, "review_text": "Black screen crash on 4K MKV HEVC video", "effective_category": "Bugs and crashes"},
        {"review_id": "r2", "rating": 1, "review_text": "Audio plays but blank screen freeze codec error", "effective_category": "Bugs and crashes"},
        {"review_id": "r3", "rating": 2, "review_text": "Too many ads popup during VR cardboard mode", "effective_category": "Advertising and monetization"},
    ])
    items = derive_opportunities_from_reviews(df)
    assert len(items) >= 2
    assert items[0].priority_score > 0
    assert len(items[0].supporting_quotes) > 0
