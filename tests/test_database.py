"""
tests/test_database.py
Tests for SQLite persistence, CRUD operations, manual overrides, and query filtering.
"""

import tempfile
from pathlib import Path
from datetime import date
from src.database import DatabaseManager
from src.models import ReviewRecord, CompetitorApp, OpportunityItem


def test_database_crud_and_overrides():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_app_radar.db"
        db = DatabaseManager(str(db_path))

        # 1. Insert review
        review = ReviewRecord(
            review_id="rev_test_01",
            app_name="VR Test",
            app_identifier="com.test.vr",
            review_date=date(2026, 10, 20),
            rating=1,
            review_text="Black screen crash on 4K playback",
            category="Bugs and crashes",
            is_synthetic=True,
        )
        res = db.save_reviews([review])
        assert res["inserted"] == 1

        # 2. Query DataFrame
        df = db.get_reviews_df(app_identifier="com.test.vr")
        assert len(df) == 1
        assert df.iloc[0]["category"] == "Bugs and crashes"
        assert df.iloc[0]["effective_category"] == "Bugs and crashes"

        # 3. Manual override of category
        success = db.update_review_category("rev_test_01", "Performance")
        assert success is True

        df_updated = db.get_reviews_df(app_identifier="com.test.vr")
        assert df_updated.iloc[0]["user_corrected_category"] == "Performance"
        assert df_updated.iloc[0]["effective_category"] == "Performance"

        # 4. Competitor insertion
        comp = CompetitorApp(
            competitor_id="comp_01",
            app_name="Competitor Pro",
            app_identifier="com.comp.pro",
            rating=4.5,
            total_reviews=12000,
            strengths=["Smooth 60fps", "Zero ads"],
            weaknesses=["High battery drain"],
        )
        db.save_competitors([comp])
        comps = db.get_competitors()
        assert len(comps) == 1
        assert comps[0].app_identifier == "com.comp.pro"

        # 5. Opportunity persistence
        opp = OpportunityItem(
            item_id="opp_01",
            title="Fix Black Screen",
            category="Bugs and crashes",
            description="ExoPlayer fallback required",
            frequency=4,
            severity=5,
            affected_users=3,
            strategic_relevance=5,
            implementation_effort=2,
            evidence_strength=4,
            confidence_multiplier=0.9,
            priority_score=12.5,
            proposed_action="Add software decoder fallback",
            strategic_category="High-Impact Project",
        )
        db.save_opportunities([opp])
        saved_opps = db.get_opportunities()
        assert len(saved_opps) == 1
        assert saved_opps[0].title == "Fix Black Screen"
