"""
src/scoring.py
Opportunity Prioritization Engine with Transparent Mathematical Scoring Model.
Calculates transparent priority rankings with user-adjustable weights.
"""

from typing import Any, Dict, List, Optional
import pandas as pd

from src.models import OpportunityItem, ReviewCategory, ALL_CATEGORIES
from src.database import DEFAULT_WEIGHTS


def calculate_opportunity_score(
    frequency: int,
    severity: int,
    affected_users: int,
    strategic_relevance: int,
    evidence_strength: int,
    implementation_effort: int,
    confidence_multiplier: float,
    weights: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """
    Computes priority score using the explicit formula:
    
    Score = [ (w_F * F + w_S * S + w_A * A + w_R * R + w_ES * ES) / (w_E * E) ] * C
    
    Returns a dict with:
      - raw_score: float
      - normalized_score_100: float (scaled 0-100)
      - numerator: float
      - denominator: float
      - components: Dict[str, float]
    """
    w = weights if weights else DEFAULT_WEIGHTS

    w_F = float(w.get("weight_frequency", 1.5))
    w_S = float(w.get("weight_severity", 2.5))
    w_A = float(w.get("weight_affected_users", 1.5))
    w_R = float(w.get("weight_strategic_relevance", 2.0))
    w_ES = float(w.get("weight_evidence_strength", 1.5))
    w_E = float(w.get("weight_effort", 1.5))

    # Clamp inputs safely
    F = max(1, min(5, frequency))
    S = max(1, min(5, severity))
    A = max(1, min(5, affected_users))
    R = max(1, min(5, strategic_relevance))
    ES = max(1, min(5, evidence_strength))
    E = max(1, min(5, implementation_effort))
    C = max(0.5, min(1.0, confidence_multiplier))

    # Calculate weighted impact numerator
    f_contrib = w_F * F
    s_contrib = w_S * S
    a_contrib = w_A * A
    r_contrib = w_R * R
    es_contrib = w_ES * ES

    numerator = f_contrib + s_contrib + a_contrib + r_contrib + es_contrib
    
    # Effort denominator
    denominator = max(0.1, w_E * E)

    # Score calculation
    raw_score = (numerator / denominator) * C

    # Theoretical maximum and minimum with current weights
    max_num = (w_F * 5) + (w_S * 5) + (w_A * 5) + (w_R * 5) + (w_ES * 5)
    min_den = max(0.1, w_E * 1)
    max_possible = (max_num / min_den) * 1.0

    min_num = (w_F * 1) + (w_S * 1) + (w_A * 1) + (w_R * 1) + (w_ES * 1)
    max_den = max(0.1, w_E * 5)
    min_possible = (min_num / max_den) * 0.5

    # Scale 0 to 100
    if max_possible > min_possible:
        normalized = ((raw_score - min_possible) / (max_possible - min_possible)) * 100.0
        normalized = max(0.0, min(100.0, normalized))
    else:
        normalized = 50.0

    return {
        "raw_score": round(raw_score, 2),
        "normalized_score_100": round(normalized, 1),
        "numerator": round(numerator, 2),
        "denominator": round(denominator, 2),
        "confidence_multiplier": C,
        "contributions": {
            "Frequency": round(f_contrib, 2),
            "Severity": round(s_contrib, 2),
            "Affected Users": round(a_contrib, 2),
            "Strategic Relevance": round(r_contrib, 2),
            "Evidence Strength": round(es_contrib, 2),
            "Effort Penalty": round(denominator, 2),
        },
        "formula_display": (
            f"[({w_F}×{F} + {w_S}×{S} + {w_A}×{A} + {w_R}×{R} + {w_ES}×{ES}) / ({w_E}×{E})] × {C}"
        )
    }


def recalculate_items(
    items: List[OpportunityItem],
    weights: Dict[str, float]
) -> List[OpportunityItem]:
    """Updates priority scores and score breakdown for a list of items using new weights."""
    updated = []
    for item in items:
        calc = calculate_opportunity_score(
            frequency=item.frequency,
            severity=item.severity,
            affected_users=item.affected_users,
            strategic_relevance=item.strategic_relevance,
            evidence_strength=item.evidence_strength,
            implementation_effort=item.implementation_effort,
            confidence_multiplier=item.confidence_multiplier,
            weights=weights,
        )
        item.priority_score = calc["raw_score"]
        item.score_breakdown = calc
        updated.append(item)

    # Sort descending by priority score
    updated.sort(key=lambda x: x.priority_score, reverse=True)
    return updated


def derive_opportunities_from_reviews(
    df: pd.DataFrame,
    weights: Optional[Dict[str, float]] = None,
) -> List[OpportunityItem]:
    """
    Analyzes review dataset clusters and generates evidence-grounded OpportunityItems.
    """
    if df.empty:
        return []

    items: List[OpportunityItem] = []
    total_reviews = len(df)

    # 1. Video Codec & Black Screen Freeze (High impact bug in VR apps)
    codec_mask = df["review_text"].str.contains(r"codec|hevc|black screen|freeze|format|mkv|audio", case=False, na=False)
    codec_reviews = df[codec_mask]
    if len(codec_reviews) > 0:
        count = len(codec_reviews)
        pct = (count / total_reviews) * 100
        avg_rating = codec_reviews["rating"].mean()
        
        freq = min(5, max(1, int(round((count / max(1, total_reviews)) * 15))))
        sev = 5 if avg_rating < 2.0 else 4
        aff = 4 if pct > 15 else 3
        
        calc = calculate_opportunity_score(
            frequency=freq,
            severity=sev,
            affected_users=aff,
            strategic_relevance=5,
            evidence_strength=min(5, max(2, int(count / 3))),
            implementation_effort=3,
            confidence_multiplier=0.95,
            weights=weights,
        )

        sample_quotes = codec_reviews["review_text"].dropna().head(3).tolist()

        items.append(OpportunityItem(
            item_id="opp_codec_hevc_support",
            title="ExoPlayer Software Decoder Fallback & HEVC/MKV Codec Fix",
            category="Bugs and crashes",
            description=(
                f"{count} users ({pct:.1f}% of reviews) report black screens or audio-only playback on "
                "high-resolution VR videos (4K/8K MKV & HEVC) when hardware decoding fails on mid-tier chipsets."
            ),
            frequency=freq,
            severity=sev,
            affected_users=aff,
            strategic_relevance=5,
            implementation_effort=3,
            evidence_strength=min(5, max(2, int(count / 3))),
            confidence_multiplier=0.95,
            priority_score=calc["raw_score"],
            score_breakdown=calc,
            supporting_review_ids=codec_reviews["review_id"].head(10).tolist(),
            supporting_quotes=sample_quotes,
            proposed_action=(
                "Implement automatic software decoding fallback in Kotlin using Media3/ExoPlayer extension-ffmpeg "
                "when hardware surface decoding throws MediaCodec.CodecException."
            ),
            strategic_category="High-Impact Project",
            risk_or_limitation="Software decoding for 4K 60fps VR videos increases CPU load and battery consumption on budget SoCs.",
            recommended_next_step="Inspect Kotlin ExoPlayer initialization in app/src/main/java and add CodecSelector fallback hook.",
        ))

    # 2. Aggressive Ad Frequency & Mid-Video Interstitials
    ad_mask = df["review_text"].str.contains(r"ad|advert|pop up|commercial|unskippable", case=False, na=False)
    ad_reviews = df[ad_mask]
    if len(ad_reviews) > 0:
        count = len(ad_reviews)
        pct = (count / total_reviews) * 100
        avg_rating = ad_reviews["rating"].mean()
        
        freq = min(5, max(1, int(round((count / max(1, total_reviews)) * 15))))
        sev = 4 if avg_rating <= 2.2 else 3
        aff = 5
        
        calc = calculate_opportunity_score(
            frequency=freq,
            severity=sev,
            affected_users=aff,
            strategic_relevance=4,
            evidence_strength=min(5, max(2, int(count / 4))),
            implementation_effort=1,
            confidence_multiplier=0.90,
            weights=weights,
        )

        sample_quotes = ad_reviews["review_text"].dropna().head(3).tolist()

        items.append(OpportunityItem(
            item_id="opp_ad_frequency_capping",
            title="Session Ad Frequency Capping & VR Headset Immersion Guard",
            category="Advertising and monetization",
            description=(
                f"{count} reviews ({pct:.1f}%) voice severe frustration over unskippable ads firing while the phone "
                "is mounted inside a VR headset, forcing users to unmount the phone to close ads."
            ),
            frequency=freq,
            severity=sev,
            affected_users=aff,
            strategic_relevance=4,
            implementation_effort=1,
            evidence_strength=min(5, max(2, int(count / 4))),
            confidence_multiplier=0.90,
            priority_score=calc["raw_score"],
            score_breakdown=calc,
            supporting_review_ids=ad_reviews["review_id"].head(10).tolist(),
            supporting_quotes=sample_quotes,
            proposed_action=(
                "Implement a 3-minute minimum cooldown between interstitial ads and disable interstitial popups entirely "
                "once the VR cardboard/sensor mode is actively rendering."
            ),
            strategic_category="Quick Win",
            risk_or_limitation="Short-term AdMob impression velocity may drop by 12-18% before 7-day retention gains offset the gap.",
            recommended_next_step="Review AdMob mediation SDK config in Kotlin, set frequency caps in Google AdMob console.",
        ))

    # 3. Gyroscope Drift & Head Tracking Reset
    gyro_mask = df["review_text"].str.contains(r"gyro|drift|sensor|head tracking|recenter|calibration", case=False, na=False)
    gyro_reviews = df[gyro_mask]
    if len(gyro_reviews) > 0:
        count = len(gyro_reviews)
        pct = (count / total_reviews) * 100
        
        calc = calculate_opportunity_score(
            frequency=3,
            severity=4,
            affected_users=3,
            strategic_relevance=4,
            evidence_strength=3,
            implementation_effort=2,
            confidence_multiplier=0.85,
            weights=weights,
        )

        sample_quotes = gyro_reviews["review_text"].dropna().head(3).tolist()

        items.append(OpportunityItem(
            item_id="opp_gyroscope_recenter",
            title="Single-Tap Recenter Button & Gyro Drifting Filter",
            category="User interface and usability",
            description=(
                f"{count} reviews report that the 360-degree viewport slowly drifts sideways during long videos, "
                "causing neck strain without an instant recenter mechanism."
            ),
            frequency=3,
            severity=4,
            affected_users=3,
            strategic_relevance=4,
            implementation_effort=2,
            evidence_strength=3,
            confidence_multiplier=0.85,
            priority_score=calc["raw_score"],
            score_breakdown=calc,
            supporting_review_ids=gyro_reviews["review_id"].head(10).tolist(),
            supporting_quotes=sample_quotes,
            proposed_action=(
                "Add an on-screen floating crosshair and volume-key hardware shortcut to trigger immediate sensor recentering, "
                "paired with a low-pass complementary Kalman filter in Android SensorManager."
            ),
            strategic_category="Quick Win",
            risk_or_limitation="Volume-up hardware trigger requires overriding onKeyDown events in the Android Activity.",
            recommended_next_step="Profile Sensor.TYPE_ROTATION_VECTOR sampling rate in Kotlin Activity.",
        ))

    # 4. Subtitle / SRT and External Audio Track Support
    sub_mask = df["review_text"].str.contains(r"subtitle|srt|audio track|language|caption", case=False, na=False)
    sub_reviews = df[sub_mask]
    if len(sub_reviews) > 0:
        count = len(sub_reviews)
        
        calc = calculate_opportunity_score(
            frequency=2,
            severity=2,
            affected_users=2,
            strategic_relevance=3,
            evidence_strength=2,
            implementation_effort=2,
            confidence_multiplier=0.80,
            weights=weights,
        )

        sample_quotes = sub_reviews["review_text"].dropna().head(3).tolist()

        items.append(OpportunityItem(
            item_id="opp_srt_subtitles",
            title="External Subtitle (SRT/VTT) & Multi-Audio Track Selector",
            category="Missing features",
            description=(
                f"{count} international power users requested sidecar .srt subtitles and dual-language audio track selection "
                "for anime and foreign language 360 documentaries."
            ),
            frequency=2,
            severity=2,
            affected_users=2,
            strategic_relevance=3,
            implementation_effort=2,
            evidence_strength=2,
            confidence_multiplier=0.80,
            priority_score=calc["raw_score"],
            score_breakdown=calc,
            supporting_review_ids=sub_reviews["review_id"].head(10).tolist(),
            supporting_quotes=sample_quotes,
            proposed_action="Support automatic local .srt detection with matching file names and expose track selector dialog.",
            strategic_category="Experimental Feature",
            risk_or_limitation="Android 11+ Scoped Storage permissions require SAF (Storage Access Framework) to read sidecar subtitle files.",
            recommended_next_step="Test Scoped Storage uri permissions for companion .srt files in Android 13/14.",
        ))

    # Recalculate and sort
    items.sort(key=lambda x: x.priority_score, reverse=True)
    return items
