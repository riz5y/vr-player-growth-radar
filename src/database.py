"""
src/database.py
Local SQLite Database Persistence Layer for App Opportunity Radar.
"""

import json
import os
import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

from src.models import (
    ReviewRecord,
    CompetitorApp,
    OpportunityItem,
    AIRecommendation,
    ALL_CATEGORIES,
)

DEFAULT_DB_DIR = Path(__file__).resolve().parent.parent / "data"
DEFAULT_DB_PATH = DEFAULT_DB_DIR / "app_radar.db"

DEFAULT_WEIGHTS = {
    "weight_frequency": 1.5,
    "weight_severity": 2.5,
    "weight_affected_users": 1.5,
    "weight_strategic_relevance": 2.0,
    "weight_evidence_strength": 1.5,
    "weight_effort": 1.5,
}


class DatabaseManager:
    """Manages SQLite operations for App Opportunity Radar with explicit connection cleanup."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path:
            self.db_path = Path(db_path)
        else:
            self.db_path = DEFAULT_DB_PATH
        
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        """Creates tables, indices, and default configurations if not present."""
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()

                # Reviews Table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS reviews (
                        review_id TEXT PRIMARY KEY,
                        app_name TEXT NOT NULL,
                        app_identifier TEXT NOT NULL,
                        review_date TEXT NOT NULL,
                        rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
                        review_text TEXT NOT NULL,
                        review_language TEXT DEFAULT 'en',
                        source TEXT DEFAULT 'google_play',
                        developer_reply TEXT,
                        is_synthetic INTEGER DEFAULT 0,
                        category TEXT NOT NULL,
                        user_corrected_category TEXT,
                        sentiment_score REAL DEFAULT 0.0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)

                # Indices for rapid filtering
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_reviews_app ON reviews (app_identifier);")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_reviews_date ON reviews (review_date);")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_reviews_category ON reviews (category);")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_reviews_rating ON reviews (rating);")

                # Competitors Table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS competitors (
                        competitor_id TEXT PRIMARY KEY,
                        app_name TEXT NOT NULL,
                        app_identifier TEXT NOT NULL UNIQUE,
                        rating REAL NOT NULL,
                        total_reviews INTEGER DEFAULT 0,
                        primary_category TEXT DEFAULT 'Video Players & Editors',
                        strengths_json TEXT,
                        weaknesses_json TEXT,
                        praised_features_json TEXT,
                        positioning_summary TEXT,
                        is_synthetic INTEGER DEFAULT 1,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)

                # Opportunity Items Table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS opportunity_items (
                        item_id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        category TEXT NOT NULL,
                        description TEXT NOT NULL,
                        frequency INTEGER NOT NULL,
                        severity INTEGER NOT NULL,
                        affected_users INTEGER NOT NULL,
                        strategic_relevance INTEGER NOT NULL,
                        implementation_effort INTEGER NOT NULL,
                        evidence_strength INTEGER NOT NULL,
                        confidence_multiplier REAL NOT NULL,
                        priority_score REAL NOT NULL,
                        score_breakdown_json TEXT,
                        supporting_review_ids_json TEXT,
                        supporting_quotes_json TEXT,
                        proposed_action TEXT NOT NULL,
                        strategic_category TEXT NOT NULL,
                        risk_or_limitation TEXT,
                        recommended_next_step TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)

                # Settings Table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS app_settings (
                        key TEXT PRIMARY KEY,
                        value_json TEXT NOT NULL
                    );
                """)
        finally:
            conn.close()

        # Seed default weights if not present
        if not self.get_setting("prioritization_weights"):
            self.save_setting("prioritization_weights", DEFAULT_WEIGHTS)

    # -------------------------------------------------------------
    # Review Management
    # -------------------------------------------------------------
    def save_reviews(self, reviews: List[ReviewRecord]) -> Dict[str, int]:
        """Inserts or updates review records."""
        inserted = 0
        existing = 0

        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                for r in reviews:
                    date_str = r.review_date.isoformat() if isinstance(r.review_date, (date, datetime)) else str(r.review_date)
                    
                    cursor.execute("SELECT review_id, user_corrected_category FROM reviews WHERE review_id = ?", (r.review_id,))
                    row = cursor.fetchone()

                    if row:
                        existing += 1
                        existing_correction = row["user_corrected_category"]
                        if existing_correction and not r.user_corrected_category:
                            r.user_corrected_category = existing_correction
                        
                        cursor.execute("""
                            UPDATE reviews SET
                                app_name = ?,
                                app_identifier = ?,
                                review_date = ?,
                                rating = ?,
                                review_text = ?,
                                review_language = ?,
                                source = ?,
                                developer_reply = ?,
                                is_synthetic = ?,
                                category = ?,
                                user_corrected_category = ?,
                                sentiment_score = ?
                            WHERE review_id = ?
                        """, (
                            r.app_name,
                            r.app_identifier,
                            date_str,
                            r.rating,
                            r.review_text,
                            r.review_language,
                            r.source,
                            r.developer_reply,
                            1 if r.is_synthetic else 0,
                            r.category,
                            r.user_corrected_category,
                            r.sentiment_score,
                            r.review_id,
                        ))
                    else:
                        cursor.execute("""
                            INSERT INTO reviews (
                                review_id, app_name, app_identifier, review_date, rating,
                                review_text, review_language, source, developer_reply,
                                is_synthetic, category, user_corrected_category, sentiment_score
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            r.review_id,
                            r.app_name,
                            r.app_identifier,
                            date_str,
                            r.rating,
                            r.review_text,
                            r.review_language,
                            r.source,
                            r.developer_reply,
                            1 if r.is_synthetic else 0,
                            r.category,
                            r.user_corrected_category,
                            r.sentiment_score,
                        ))
                        inserted += 1
        finally:
            conn.close()

        return {"inserted": inserted, "updated": existing, "total_processed": len(reviews)}

    def get_reviews_df(
        self,
        app_identifier: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        category: Optional[str] = None,
        min_rating: Optional[int] = None,
        max_rating: Optional[int] = None,
        search_query: Optional[str] = None,
    ) -> pd.DataFrame:
        """Queries reviews from SQLite and returns a pandas DataFrame with computed effective category."""
        query = "SELECT * FROM reviews WHERE 1=1"
        params: List[Any] = []

        if app_identifier and app_identifier != "All Apps":
            query += " AND app_identifier = ?"
            params.append(app_identifier)

        if start_date:
            query += " AND review_date >= ?"
            params.append(str(start_date))

        if end_date:
            query += " AND review_date <= ?"
            params.append(str(end_date))

        if category and category != "All Categories":
            query += " AND COALESCE(user_corrected_category, category) = ?"
            params.append(category)

        if min_rating is not None:
            query += " AND rating >= ?"
            params.append(min_rating)

        if max_rating is not None:
            query += " AND rating <= ?"
            params.append(max_rating)

        if search_query and search_query.strip():
            query += " AND review_text LIKE ?"
            params.append(f"%{search_query.strip()}%")

        query += " ORDER BY review_date DESC"

        conn = self.get_connection()
        try:
            df = pd.read_sql_query(query, conn, params=params)
        finally:
            conn.close()

        if not df.empty:
            df["review_date"] = pd.to_datetime(df["review_date"])
            df["effective_category"] = df["user_corrected_category"].fillna(df["category"])
            df["is_synthetic"] = df["is_synthetic"].astype(bool)

        return df

    def update_review_category(self, review_id: str, new_category: str) -> bool:
        """Updates the manual user-corrected category for a single review."""
        if new_category not in ALL_CATEGORIES:
            raise ValueError(f"Category '{new_category}' is not valid. Choose from {ALL_CATEGORIES}")

        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE reviews SET user_corrected_category = ? WHERE review_id = ?",
                    (new_category, review_id),
                )
                return cursor.rowcount > 0
        finally:
            conn.close()

    def get_distinct_apps(self) -> List[Dict[str, str]]:
        """Returns list of distinct apps present in the reviews database."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT app_identifier, app_name, COUNT(*) as review_count, AVG(rating) as avg_rating
                FROM reviews
                GROUP BY app_identifier, app_name
                ORDER BY review_count DESC
            """)
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def clear_reviews(self, synthetic_only: bool = False) -> int:
        """Deletes reviews from the database."""
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                if synthetic_only:
                    cursor.execute("DELETE FROM reviews WHERE is_synthetic = 1")
                else:
                    cursor.execute("DELETE FROM reviews")
                return cursor.rowcount
        finally:
            conn.close()

    # -------------------------------------------------------------
    # Competitor Management
    # -------------------------------------------------------------
    def save_competitors(self, competitors: List[CompetitorApp]) -> None:
        """Saves competitor apps to SQLite."""
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                for c in competitors:
                    cursor.execute("""
                        INSERT INTO competitors (
                            competitor_id, app_name, app_identifier, rating, total_reviews,
                            primary_category, strengths_json, weaknesses_json,
                            praised_features_json, positioning_summary, is_synthetic, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                        ON CONFLICT(competitor_id) DO UPDATE SET
                            app_name=excluded.app_name,
                            app_identifier=excluded.app_identifier,
                            rating=excluded.rating,
                            total_reviews=excluded.total_reviews,
                            primary_category=excluded.primary_category,
                            strengths_json=excluded.strengths_json,
                            weaknesses_json=excluded.weaknesses_json,
                            praised_features_json=excluded.praised_features_json,
                            positioning_summary=excluded.positioning_summary,
                            is_synthetic=excluded.is_synthetic,
                            updated_at=CURRENT_TIMESTAMP
                    """, (
                        c.competitor_id,
                        c.app_name,
                        c.app_identifier,
                        c.rating,
                        c.total_reviews,
                        c.primary_category,
                        json.dumps(c.strengths),
                        json.dumps(c.weaknesses),
                        json.dumps(c.praised_features),
                        c.positioning_summary,
                        1 if c.is_synthetic else 0,
                    ))
        finally:
            conn.close()

    def get_competitors(self) -> List[CompetitorApp]:
        """Returns list of all competitor records."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM competitors ORDER BY rating DESC")
            rows = cursor.fetchall()
            competitors = []
            for row in rows:
                c = CompetitorApp(
                    competitor_id=row["competitor_id"],
                    app_name=row["app_name"],
                    app_identifier=row["app_identifier"],
                    rating=row["rating"],
                    total_reviews=row["total_reviews"],
                    primary_category=row["primary_category"],
                    strengths=json.loads(row["strengths_json"]) if row["strengths_json"] else [],
                    weaknesses=json.loads(row["weaknesses_json"]) if row["weaknesses_json"] else [],
                    praised_features=json.loads(row["praised_features_json"]) if row["praised_features_json"] else [],
                    positioning_summary=row["positioning_summary"] or "",
                    is_synthetic=bool(row["is_synthetic"]),
                )
                competitors.append(c)
            return competitors
        finally:
            conn.close()

    # -------------------------------------------------------------
    # Opportunity Items Management
    # -------------------------------------------------------------
    def save_opportunities(self, items: List[OpportunityItem]) -> None:
        """Saves scored opportunity items."""
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                for item in items:
                    cursor.execute("""
                        INSERT INTO opportunity_items (
                            item_id, title, category, description, frequency, severity,
                            affected_users, strategic_relevance, implementation_effort,
                            evidence_strength, confidence_multiplier, priority_score,
                            score_breakdown_json, supporting_review_ids_json,
                            supporting_quotes_json, proposed_action, strategic_category,
                            risk_or_limitation, recommended_next_step, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                        ON CONFLICT(item_id) DO UPDATE SET
                            title=excluded.title,
                            category=excluded.category,
                            description=excluded.description,
                            frequency=excluded.frequency,
                            severity=excluded.severity,
                            affected_users=excluded.affected_users,
                            strategic_relevance=excluded.strategic_relevance,
                            implementation_effort=excluded.implementation_effort,
                            evidence_strength=excluded.evidence_strength,
                            confidence_multiplier=excluded.confidence_multiplier,
                            priority_score=excluded.priority_score,
                            score_breakdown_json=excluded.score_breakdown_json,
                            supporting_review_ids_json=excluded.supporting_review_ids_json,
                            supporting_quotes_json=excluded.supporting_quotes_json,
                            proposed_action=excluded.proposed_action,
                            strategic_category=excluded.strategic_category,
                            risk_or_limitation=excluded.risk_or_limitation,
                            recommended_next_step=excluded.recommended_next_step,
                            updated_at=CURRENT_TIMESTAMP
                    """, (
                        item.item_id,
                        item.title,
                        item.category,
                        item.description,
                        item.frequency,
                        item.severity,
                        item.affected_users,
                        item.strategic_relevance,
                        item.implementation_effort,
                        item.evidence_strength,
                        item.confidence_multiplier,
                        item.priority_score,
                        json.dumps(item.score_breakdown),
                        json.dumps(item.supporting_review_ids),
                        json.dumps(item.supporting_quotes),
                        item.proposed_action,
                        item.strategic_category,
                        item.risk_or_limitation,
                        item.recommended_next_step,
                    ))
        finally:
            conn.close()

    def get_opportunities(self) -> List[OpportunityItem]:
        """Loads all opportunity items ordered by priority_score descending."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM opportunity_items ORDER BY priority_score DESC")
            rows = cursor.fetchall()
            items = []
            for row in rows:
                item = OpportunityItem(
                    item_id=row["item_id"],
                    title=row["title"],
                    category=row["category"],
                    description=row["description"],
                    frequency=row["frequency"],
                    severity=row["severity"],
                    affected_users=row["affected_users"],
                    strategic_relevance=row["strategic_relevance"],
                    implementation_effort=row["implementation_effort"],
                    evidence_strength=row["evidence_strength"],
                    confidence_multiplier=row["confidence_multiplier"],
                    priority_score=row["priority_score"],
                    score_breakdown=json.loads(row["score_breakdown_json"]) if row["score_breakdown_json"] else {},
                    supporting_review_ids=json.loads(row["supporting_review_ids_json"]) if row["supporting_review_ids_json"] else [],
                    supporting_quotes=json.loads(row["supporting_quotes_json"]) if row["supporting_quotes_json"] else [],
                    proposed_action=row["proposed_action"],
                    strategic_category=row["strategic_category"],
                    risk_or_limitation=row["risk_or_limitation"] or "",
                    recommended_next_step=row["recommended_next_step"] or "",
                )
                items.append(item)
            return items
        finally:
            conn.close()

    # -------------------------------------------------------------
    # Settings & Key-Value Configuration
    # -------------------------------------------------------------
    def get_setting(self, key: str, default: Any = None) -> Any:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT value_json FROM app_settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            if row:
                try:
                    return json.loads(row["value_json"])
                except Exception:
                    return row["value_json"]
            return default
        finally:
            conn.close()

    def save_setting(self, key: str, value: Any) -> None:
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                value_json = json.dumps(value)
                cursor.execute("""
                    INSERT INTO app_settings (key, value_json) VALUES (?, ?)
                    ON CONFLICT(key) DO UPDATE SET value_json = excluded.value_json
                """, (key, value_json))
        finally:
            conn.close()

    def get_database_stats(self) -> Dict[str, Any]:
        """Returns aggregate metrics for system health display."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM reviews")
            total_reviews = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM reviews WHERE is_synthetic = 1")
            synthetic_reviews = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM competitors")
            total_competitors = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM opportunity_items")
            total_opportunities = cursor.fetchone()[0]

            cursor.execute("SELECT AVG(rating) FROM reviews")
            avg_rating_row = cursor.fetchone()[0]
            avg_rating = round(avg_rating_row, 2) if avg_rating_row else 0.0

            return {
                "total_reviews": total_reviews,
                "real_reviews": total_reviews - synthetic_reviews,
                "synthetic_reviews": synthetic_reviews,
                "avg_rating": avg_rating,
                "total_competitors": total_competitors,
                "total_opportunities": total_opportunities,
                "db_path": str(self.db_path),
            }
        finally:
            conn.close()
