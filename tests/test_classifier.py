"""
tests/test_classifier.py
Unit tests verifying the 9-bucket review classification and sentiment scoring.
"""

from src.classifier import classify_review_text, compute_sentiment_score
from src.models import (
    CATEGORY_BUGS_CRASHES,
    CATEGORY_PERFORMANCE,
    CATEGORY_UI_USABILITY,
    CATEGORY_ADS_MONETIZATION,
    CATEGORY_MISSING_FEATURES,
    CATEGORY_ACCOUNT_ONBOARDING,
    CATEGORY_PRICING_SUBSCRIPTIONS,
    CATEGORY_POSITIVE_FEEDBACK,
    CATEGORY_OTHER,
    ALL_CATEGORIES,
)


def test_classifier_all_nine_categories_covered():
    """Verifies that all 9 required categories can be assigned."""
    test_cases = [
        ("The app crashes with a black screen every time I open it", 1, CATEGORY_BUGS_CRASHES),
        ("Super laggy, drops frames and causes terrible motion sickness and stuttering", 2, CATEGORY_PERFORMANCE),
        ("The UI buttons are confusing and head tracking gyroscope drifts constantly", 2, CATEGORY_UI_USABILITY),
        ("Unbearable ads popping up every 30 seconds while in VR headset", 1, CATEGORY_ADS_MONETIZATION),
        ("Please add SRT subtitles and MKV support, we really need this feature", 3, CATEGORY_MISSING_FEATURES),
        ("Cannot login or signup, account verification code never arrives", 1, CATEGORY_ACCOUNT_ONBOARDING),
        ("Too expensive subscription, predatory paywall for basic features", 2, CATEGORY_PRICING_SUBSCRIPTIONS),
        ("Superb player! Smooth playback, best VR experience ever, love it", 5, CATEGORY_POSITIVE_FEEDBACK),
        ("Just a standard video app, nothing special", 3, CATEGORY_OTHER),
    ]

    for text, rating, expected_cat in test_cases:
        cat, conf = classify_review_text(text, rating)
        assert cat in ALL_CATEGORIES
        assert cat == expected_cat, f"Expected '{expected_cat}', got '{cat}' for text: '{text}'"
        assert 0.0 <= conf <= 1.0


def test_classifier_negation_handling():
    """Ensures phrases like 'no bugs' and 'never crashed' are not labeled as crashes."""
    text = "Great player, absolutely no bugs and never crashed, love it!"
    cat, conf = classify_review_text(text, rating=5)
    assert cat == CATEGORY_POSITIVE_FEEDBACK


def test_sentiment_score_bounds_and_polarity():
    """Ensures sentiment scoring stays bounded in [-1.0, 1.0] and aligns with star rating."""
    neg_score = compute_sentiment_score("Horrible, terrible, worst app ever broken trash", 1)
    assert neg_score <= -0.5

    pos_score = compute_sentiment_score("Flawless, fantastic, smooth, beautiful and perfect", 5)
    assert pos_score >= 0.5

    neutral_score = compute_sentiment_score("It plays files normally.", 3)
    assert -0.3 <= neutral_score <= 0.3
