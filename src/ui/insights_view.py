"""
src/ui/insights_view.py
Section 3: AI Insights & Recommendations.
Displays structured, evidence-grounded recommendations with explicit next steps and risk assessments.
"""

import streamlit as st
import pandas as pd
from src.database import DatabaseManager
from src.ai_analyzer import AIAnalyzerEngine


def render_insights_view(db: DatabaseManager, selected_app_id: str):
    st.markdown("## 🧠 AI Insights & Evidence-Grounded Recommendations")
    st.markdown(
        "<p style='color: #94a3b8; font-size: 0.95rem; margin-top: -10px;'>"
        "Actionable growth and product recommendations grounded strictly in verified store feedback."
        "</p>",
        unsafe_allow_html=True
    )

    df = db.get_reviews_df(app_identifier=selected_app_id)
    if df.empty:
        st.warning("No review records found in database. Ingest a dataset first.")
        return

    analyzer = AIAnalyzerEngine()
    recommendations = analyzer.generate_recommendations(df, app_name=df.iloc[0]["app_name"], app_identifier=selected_app_id)

    if not recommendations:
        st.info("No recommendations could be generated from the available review sample.")
        return

    # Strategic category filter
    tier_filter = st.radio(
        "Filter by Strategic Category:",
        ["All Strategic Tiers", "Quick Win", "High-Impact Project", "Defensive Fix", "Experimental Feature"],
        horizontal=True
    )

    filtered_recs = [
        r for r in recommendations
        if tier_filter == "All Strategic Tiers" or r.strategic_category == tier_filter
    ]

    tier_classes = {
        "Quick Win": "tier-quick-win",
        "High-Impact Project": "tier-high-impact",
        "Defensive Fix": "tier-defensive",
        "Experimental Feature": "tier-experimental",
    }

    for rec in filtered_recs:
        badge_cls = tier_classes.get(rec.strategic_category, "badge-other")
        pattern_badge = (
            "<span class='badge' style='background: rgba(16, 185, 129, 0.15); color: #34d399;'>Verified Pattern</span>"
            if rec.is_verified_pattern
            else "<span class='badge' style='background: rgba(168, 85, 247, 0.15); color: #c084fc;'>Exploratory Hypothesis</span>"
        )

        st.markdown(f"""
        <div class="radar-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
                <div>
                    <span class="badge {badge_cls}">{rec.strategic_category}</span>
                    {pattern_badge}
                    <span class="badge" style="background: rgba(255,255,255,0.08); color: #e2e8f0; margin-left: 4px;">
                        Confidence: {rec.confidence_level}
                    </span>
                    <h3 style="margin-top: 10px; margin-bottom: 4px; color: #ffffff; font-size: 1.18rem; font-weight: 700;">
                        {rec.summary_statement}
                    </h3>
                </div>
                <div style="text-align: right; min-width: 130px;">
                    <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase;">Supporting Data</div>
                    <div style="font-size: 1.15rem; font-weight: 800; color: #ffffff;">{rec.supporting_review_count} Reviews</div>
                    <div style="font-size: 0.8rem; color: #ef4444;">Avg: {rec.avg_rating_impact:.1f} ★</div>
                </div>
            </div>

            <div style="color: #cbd5e1; font-size: 0.93rem; line-height: 1.6; margin-bottom: 14px;">
                <strong>Problem & Opportunity:</strong> {rec.problem_or_opportunity}
            </div>

            <div style="background: rgba(0, 0, 0, 0.35); border-left: 3px solid #00f2fe; padding: 10px 14px; border-radius: 6px; margin-bottom: 14px;">
                <div style="font-size: 0.82rem; font-weight: 700; color: #00f2fe; text-transform: uppercase; margin-bottom: 2px;">
                    🧪 Proposed Action or Experiment
                </div>
                <div style="color: #e2e8f0; font-size: 0.90rem;">{rec.proposed_action_or_experiment}</div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 10px;">
                <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 6px; padding: 8px 12px;">
                    <div style="font-size: 0.75rem; font-weight: 700; color: #f87171; text-transform: uppercase;">⚠️ Risk or Limitation</div>
                    <div style="color: #fca5a5; font-size: 0.84rem; margin-top: 2px;">{rec.risk_or_limitation}</div>
                </div>
                <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 6px; padding: 8px 12px;">
                    <div style="font-size: 0.75rem; font-weight: 700; color: #34d399; text-transform: uppercase;">🛠️ Recommended Next Step</div>
                    <div style="color: #a7f3d0; font-size: 0.84rem; margin-top: 2px;">{rec.recommended_next_step}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander(f"💬 View {len(rec.sample_quotes)} Verbatim Supporting Review Quotes"):
            for q in rec.sample_quotes:
                st.markdown(f"> *\"{q}\"*")
