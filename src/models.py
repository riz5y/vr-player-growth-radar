"""
src/models.py
Pydantic Data Models and Validation Schemas for App Opportunity Radar.
"""

from datetime import date, datetime
from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


# Mandatory 9-Category Taxonomy per Project Specification
CATEGORY_BUGS_CRASHES = "Bugs and crashes"
CATEGORY_PERFORMANCE = "Performance"
CATEGORY_UI_USABILITY = "User interface and usability"
CATEGORY_ADS_MONETIZATION = "Advertising and monetization"
CATEGORY_MISSING_FEATURES = "Missing features"
CATEGORY_ACCOUNT_ONBOARDING = "Account and onboarding"
CATEGORY_PRICING_SUBSCRIPTIONS = "Pricing and subscriptions"
CATEGORY_POSITIVE_FEEDBACK = "Positive feedback"
CATEGORY_OTHER = "Other"

ALL_CATEGORIES = [
    CATEGORY_BUGS_CRASHES,
    CATEGORY_PERFORMANCE,
    CATEGORY_UI_USABILITY,
    CATEGORY_ADS_MONETIZATION,
    CATEGORY_MISSING_FEATURES,
    CATEGORY_ACCOUNT_ONBOARDING,
    CATEGORY_PRICING_SUBSCRIPTIONS,
    CATEGORY_POSITIVE_FEEDBACK,
    CATEGORY_OTHER,
]

ReviewCategory = Literal[
    "Bugs and crashes",
    "Performance",
    "User interface and usability",
    "Advertising and monetization",
    "Missing features",
    "Account and onboarding",
    "Pricing and subscriptions",
    "Positive feedback",
    "Other",
]

StrategicCategory = Literal[
    "Quick Win",
    "High-Impact Project",
    "Defensive Fix",
    "Experimental Feature",
]

ConfidenceLevel = Literal["High", "Medium", "Low", "Exploratory"]


class ReviewRecord(BaseModel):
    """
    Normalized review record adhering to the standard schema.
    """
    review_id: str = Field(..., description="Unique identifier for the review")
    app_name: str = Field(..., description="Human-readable application name")
    app_identifier: str = Field(..., description="Package name or bundle id (e.g. com.vrplayer...)")
    review_date: date = Field(..., description="Date the review was posted")
    rating: int = Field(..., ge=1, le=5, description="Star rating from 1 to 5")
    review_text: str = Field(..., description="Body of the user review")
    review_language: str = Field(default="en", description="ISO language code of the review")
    source: str = Field(default="google_play", description="Source platform (google_play, app_store, csv)")
    developer_reply: Optional[str] = Field(default=None, description="Optional developer response text")
    is_synthetic: bool = Field(default=False, description="Flag indicating if record is synthetic/demo data")
    category: ReviewCategory = Field(default="Other", description="Assigned feedback category")
    user_corrected_category: Optional[ReviewCategory] = Field(
        default=None, description="Manual correction override if user modifies category"
    )
    sentiment_score: float = Field(
        default=0.0, ge=-1.0, le=1.0, description="Heuristic polarity from -1.0 (negative) to +1.0 (positive)"
    )

    @field_validator("rating")
    @classmethod
    def validate_rating_bounds(cls, v: int) -> int:
        if v < 1 or v > 5:
            raise ValueError(f"Rating must be between 1 and 5 inclusive, got {v}")
        return v

    @property
    def effective_category(self) -> str:
        """Returns the user-corrected category if present, otherwise automated category."""
        return self.user_corrected_category or self.category


class CompetitorApp(BaseModel):
    """
    Competitor intelligence profile for benchmarking.
    """
    competitor_id: str = Field(..., description="Unique identifier")
    app_name: str = Field(..., description="Competitor app title")
    app_identifier: str = Field(..., description="Competitor package name")
    rating: float = Field(..., ge=1.0, le=5.0, description="Average store rating")
    total_reviews: int = Field(default=0, ge=0)
    primary_category: str = Field(default="Video Players & Editors")
    strengths: List[str] = Field(default_factory=list, description="Key features users praise")
    weaknesses: List[str] = Field(default_factory=list, description="Common complaints in competitor reviews")
    praised_features: List[str] = Field(default_factory=list, description="Specific features praised")
    positioning_summary: str = Field(default="", description="High-level product positioning")
    is_synthetic: bool = Field(default=True, description="Flag indicating synthetic benchmark data")


class OpportunityItem(BaseModel):
    """
    Opportunity prioritization item with explicit mathematical score components.
    """
    item_id: str = Field(..., description="Unique ID for the opportunity item")
    title: str = Field(..., description="Actionable title of problem or opportunity")
    category: ReviewCategory = Field(..., description="Associated review category")
    description: str = Field(..., description="Detailed problem or opportunity statement")
    
    # 7 Transparent Scoring Factors (1 to 5 scale, and Confidence multiplier 0.5 to 1.0)
    frequency: int = Field(..., ge=1, le=5, description="How often mentioned (1=rare, 5=everywhere)")
    severity: int = Field(..., ge=1, le=5, description="Impact on rating or blocker severity (1=minor, 5=critical)")
    affected_users: int = Field(..., ge=1, le=5, description="Estimated user base fraction impacted (1=niche, 5=all)")
    strategic_relevance: int = Field(..., ge=1, le=5, description="Business alignment with growth/retention goals (1=low, 5=core)")
    implementation_effort: int = Field(..., ge=1, le=5, description="Engineering/QA effort (1=trivial, 5=massive rewrite)")
    evidence_strength: int = Field(..., ge=1, le=5, description="Volume & quality of supporting reviews (1=anecdotal, 5=proven pattern)")
    confidence_multiplier: float = Field(..., ge=0.5, le=1.0, description="Data reliability factor (0.5=low, 1.0=verified)")
    
    # Calculated Priority Score
    priority_score: float = Field(default=0.0, description="Computed priority score based on configured weights")
    score_breakdown: Dict[str, Any] = Field(default_factory=dict, description="Detailed formula component audit")
    
    # Evidence & Action
    supporting_review_ids: List[str] = Field(default_factory=list)
    supporting_quotes: List[str] = Field(default_factory=list)
    proposed_action: str = Field(..., description="Concrete product/engineering fix or feature change")
    strategic_category: StrategicCategory = Field(default="Defensive Fix")
    risk_or_limitation: str = Field(default="", description="Risks, dependencies, or trade-offs")
    recommended_next_step: str = Field(default="", description="First step (e.g. check Kotlin ExoPlayer pipeline)")


class AIRecommendation(BaseModel):
    """
    Structured AI recommendation grounded in evidence.
    """
    id: str = Field(..., description="Unique recommendation ID")
    summary_statement: str = Field(..., description="One-line executive takeaway")
    problem_or_opportunity: str = Field(..., description="Evidence-backed description of the issue or opportunity")
    affected_user_segment: str = Field(..., description="Who experiences this (e.g. users with 4K 60fps VR videos)")
    supporting_review_count: int = Field(default=0, description="Number of supporting reviews verified")
    avg_rating_impact: float = Field(default=0.0, description="Average rating of users reporting this issue")
    sample_quotes: List[str] = Field(default_factory=list, description="Verbatim quotes from store reviews")
    proposed_action_or_experiment: str = Field(..., description="Testable hypothesis or feature experiment")
    strategic_category: StrategicCategory = Field(..., description="Strategic tier")
    risk_or_limitation: str = Field(..., description="Explicit limitation or data gap")
    recommended_next_step: str = Field(..., description="Actionable next step for engineering or product")
    confidence_level: ConfidenceLevel = Field(..., description="Confidence rating")
    is_verified_pattern: bool = Field(default=True, description="True if verified pattern, False if exploratory hypothesis")
