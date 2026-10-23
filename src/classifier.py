"""
src/classifier.py
Deterministic 9-Category Review Classifier and Sentiment Engine.
Strictly maps reviews to the 9 project-specified taxonomy buckets.
"""

import re
from typing import Tuple, Dict, List
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
    ReviewCategory,
)

# Semantic keywords and regex patterns for each category
CATEGORY_PATTERNS: Dict[str, List[str]] = {
    CATEGORY_BUGS_CRASHES: [
        r"\bcrash(ed|es|ing)?\b",
        r"\bfreeze|frozen|freezing\b",
        r"\bblack\s*screen\b",
        r"\bblank\s*screen\b",
        r"\bbug(gy|s)?\b",
        r"\bglitch(es|y)?\b",
        r"\bforce\s*close\b",
        r"\bstopped\s*working\b",
        r"\bbroken\b",
        r"\berror\b",
        r"\bfail(s|ed|ing)?\b",
        r"\bdoesn't\s*work\b",
        r"\bwon't\s*open\b",
        r"\bcan't\s*play\b",
    ],
    CATEGORY_PERFORMANCE: [
        r"\blag(gy|ging|s)?\b",
        r"\bslow\b",
        r"\bframe\s*drop(s)?\b",
        r"\bfps\b",
        r"\bstutter(ing|s)?\b",
        r"\bbuffering\b",
        r"\bheating|overheat(s|ing)?\b",
        r"\bbattery\s*drain(ing)?\b",
        r"\bmemory\s*leak\b",
        r"\bheavy\b",
        r"\bchoppy\b",
        r"\blatency\b",
        r"\bhigh\s*res\b.*(stuck|unplayable)",
    ],
    CATEGORY_UI_USABILITY: [
        r"\bui\b",
        r"\bux\b",
        r"\binterface\b",
        r"\bbutton(s)?\b",
        r"\bfont\b",
        r"\bnavigat(ion|e)\b",
        r"\bconfusing\b",
        r"\bhard\s*to\s*(use|find|navigate|control)\b",
        r"\bcluttered\b",
        r"\bugly\b",
        r"\bgvr|gyro(scope)?\s*drift\b",
        r"\bhead\s*tracking\b",
        r"\bcontrols?\b",
        r"\bgesture(s)?\b",
        r"\blandscape\b",
    ],
    CATEGORY_ADS_MONETIZATION: [
        r"\bad(s)?\b",
        r"\badvert(s|isement|ising)?\b",
        r"\bpop\s*up(s)?\b",
        r"\bcommercials?\b",
        r"\btoo\s*many\s*ads\b",
        r"\bunskippable\b",
        r"\bad\s*spam\b",
        r"\bevery\s*(click|second|minute)\b.*ad",
    ],
    CATEGORY_MISSING_FEATURES: [
        r"\bneed(s)?\b",
        r"\bplease\s*add\b",
        r"\bwish\s*it\s*had\b",
        r"\bmissing\b",
        r"\bfeature\s*request\b",
        r"\bsubtitle(s)?\b",
        r"\bsrt\b",
        r"\baudio\s*track\b",
        r"\bcodec\b",
        r"\bmkv\b",
        r"\bhevc\b",
        r"\bspatial\s*audio\b",
        r"\bcloud\s*stream(ing)?\b",
        r"\bsmb\b|\bdlna\b|\bnas\b",
    ],
    CATEGORY_ACCOUNT_ONBOARDING: [
        r"\blogin\b",
        r"\bsign\s*in\b",
        r"\bsign\s*up\b",
        r"\baccount\b",
        r"\bpassword\b",
        r"\bauth(entication)?\b",
        r"\botp\b",
        r"\bverification\b",
        r"\bonboarding\b",
        r"\btutorial\b",
        r"\bregistration\b",
        r"\bpermission(s)?\b",
    ],
    CATEGORY_PRICING_SUBSCRIPTIONS: [
        r"\bprice\b",
        r"\bexpensive\b",
        r"\bcost\b",
        r"\bsubscription\b",
        r"\bpaywall\b",
        r"\bcharge(d|s)?\b",
        r"\brefund\b",
        r"\btrial\b",
        r"\bworth\s*the\s*money\b",
        r"\brip\s*off\b",
        r"\bgreedy\b",
        r"\bpremium\b",
    ],
    CATEGORY_POSITIVE_FEEDBACK: [
        r"\bgreat\b",
        r"\bexcellent\b",
        r"\bawesome\b",
        r"\blove\s*(it|this)\b",
        r"\bbest\b",
        r"\bperfect\b",
        r"\bsmooth\b",
        r"\bworks?\s*well\b",
        r"\bfantastic\b",
        r"\bhelpful\b",
        r"\bgood\s*job\b",
        r"\bthank\s*you\b",
    ],
}

POSITIVE_WORDS = {
    "great", "excellent", "awesome", "good", "best", "love", "perfect",
    "smooth", "clean", "easy", "helpful", "superb", "brilliant", "nice",
    "recommend", "fast", "flawless", "favorite"
}

NEGATIVE_WORDS = {
    "bad", "terrible", "awful", "horrible", "worst", "hate", "trash",
    "garbage", "waste", "useless", "broken", "freeze", "crash", "lag",
    "bug", "annoying", "poor", "unusable", "greedy", "ruined"
}

NEGATION_PATTERNS = [
    r"\bno\s+bugs\b",
    r"\bnot\s+crashing\b",
    r"\bnever\s+crashed\b",
    r"\bno\s+ads\b",
    r"\bno\s+lag\b",
    r"\bwithout\s+ads\b",
    r"\bwithout\s+any\s+issues\b",
]


def compute_sentiment_score(text: str, rating: int) -> float:
    """
    Computes a normalized sentiment polarity between -1.0 (very negative) and 1.0 (very positive),
    grounded by text token analysis and anchored by the user's explicit star rating.
    """
    text_lower = text.lower()
    tokens = re.findall(r"\b\w+\b", text_lower)
    
    pos_count = sum(1 for t in tokens if t in POSITIVE_WORDS)
    neg_count = sum(1 for t in tokens if t in NEGATIVE_WORDS)
    
    total_sentiment_tokens = pos_count + neg_count
    if total_sentiment_tokens > 0:
        token_sentiment = (pos_count - neg_count) / total_sentiment_tokens
    else:
        token_sentiment = 0.0

    # Rating provides a prior anchor: 1=-1.0, 2=-0.5, 3=0.0, 4=0.5, 5=1.0
    rating_anchor = (rating - 3.0) / 2.0
    
    # Blended score: 60% star anchor, 40% textual sentiment
    blended = (0.6 * rating_anchor) + (0.4 * token_sentiment)
    return round(max(-1.0, min(1.0, blended)), 2)


def classify_review_text(text: str, rating: int) -> Tuple[ReviewCategory, float]:
    """
    Classifies review text into one of the 9 required categories.
    Returns (Category, Confidence Score).
    """
    if not text or not text.strip():
        if rating >= 4:
            return CATEGORY_POSITIVE_FEEDBACK, 0.70
        return CATEGORY_OTHER, 0.50

    text_lower = text.lower()

    # Pre-check: if high rating and explicit negation of issues (e.g. "no lag, no crashes, love it")
    has_negated_issue = any(re.search(pat, text_lower) for pat in NEGATION_PATTERNS)
    if rating >= 4 and has_negated_issue:
        return CATEGORY_POSITIVE_FEEDBACK, 0.85

    # Check for Advertising first if user explicitly complains about ads
    ad_matches = sum(1 for pat in CATEGORY_PATTERNS[CATEGORY_ADS_MONETIZATION] if re.search(pat, text_lower))
    if ad_matches >= 1 and rating <= 3:
        return CATEGORY_ADS_MONETIZATION, min(0.95, 0.70 + (0.1 * ad_matches))

    # Evaluate matches across all categories
    scores: Dict[str, float] = {}

    for cat, patterns in CATEGORY_PATTERNS.items():
        match_count = 0
        for pat in patterns:
            if re.search(pat, text_lower):
                match_count += 1
        
        if match_count > 0:
            weight = match_count * 1.0
            
            # Align with rating expectations
            if cat in [CATEGORY_BUGS_CRASHES, CATEGORY_PERFORMANCE, CATEGORY_ADS_MONETIZATION]:
                if rating <= 2:
                    weight *= 1.3
                elif rating >= 4:
                    weight *= 0.6
            elif cat == CATEGORY_POSITIVE_FEEDBACK:
                if rating >= 4:
                    weight *= 1.4
                elif rating <= 2:
                    weight *= 0.3
            elif cat == CATEGORY_MISSING_FEATURES:
                if 2 <= rating <= 4:
                    weight *= 1.2
            
            scores[cat] = weight

    if not scores:
        # Fallback heuristic based on rating
        if rating >= 4:
            return CATEGORY_POSITIVE_FEEDBACK, 0.65
        return CATEGORY_OTHER, 0.50

    # Pick category with highest matched score
    top_category = max(scores.items(), key=lambda x: x[1])
    category_name = top_category[0]
    raw_score = top_category[1]

    confidence = round(min(0.95, 0.60 + (raw_score * 0.1)), 2)

    return category_name, confidence  # type: ignore
