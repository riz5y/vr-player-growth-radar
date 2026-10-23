"""
src/ui/prioritization_view.py
Section 5: Opportunity Prioritization Engine.
Dynamic weight adjustments, mathematical ranking model, full auditability, and roadmap export.
"""

import streamlit as st
import pandas as pd
from src.database import DatabaseManager, DEFAULT_WEIGHTS
from src.scoring import recalculate_items, derive_opportunities_from_reviews


def render_prioritization_view(db: DatabaseManager, selected_app_id: str):
    st.markdown("## 🎯 Opportunity Prioritization Matrix")
    st.markdown(
        "<p style='color: #94a3b8; font-size: 0.95rem; margin-top: -10px;'>"
        "Transparent mathematical scoring engine to rank engineering and product bets."
        "</p>",
        unsafe_allow_html=True
    )

    # 1. Load weights configuration
    current_weights = db.get_setting("prioritization_weights", DEFAULT_WEIGHTS)

    # Criteria weight sliders in expander
    with st.expander("⚖️ Dynamic Criteria Weights & Formula Tuning", expanded=True):
        st.markdown(
            "$$\\text{Priority Score} = "
            "\\left( \\frac{w_F \\cdot F + w_S \\cdot S + w_A \\cdot A + w_R \\cdot R + w_{ES} \\cdot ES}{w_E \\cdot E} \\right) \\times C$$"
        )
        st.markdown("<div style='font-size: 0.82rem; color: #94a3b8;'>Adjust criteria weights to shift prioritization strategy (e.g. prioritize rating defense vs. low-effort quick wins):</div>", unsafe_allow_html=True)

        w_col1, w_col2, w_col3, w_col4, w_col5, w_col6 = st.columns(6)

        with w_col1:
            w_F = st.slider("Freq (w_F)", 0.5, 5.0, float(current_weights.get("weight_frequency", 1.5)), 0.5)
        with w_col2:
            w_S = st.slider("Severity (w_S)", 0.5, 5.0, float(current_weights.get("weight_severity", 2.5)), 0.5)
        with w_col3:
            w_A = st.slider("Users (w_A)", 0.5, 5.0, float(current_weights.get("weight_affected_users", 1.5)), 0.5)
        with w_col4:
            w_R = st.slider("Strategy (w_R)", 0.5, 5.0, float(current_weights.get("weight_strategic_relevance", 2.0)), 0.5)
        with w_col5:
            w_ES = st.slider("Evidence (w_ES)", 0.5, 5.0, float(current_weights.get("weight_evidence_strength", 1.5)), 0.5)
        with w_col6:
            w_E = st.slider("Effort Penalty (w_E)", 0.5, 5.0, float(current_weights.get("weight_effort", 1.5)), 0.5)

        new_weights = {
            "weight_frequency": w_F,
            "weight_severity": w_S,
            "weight_affected_users": w_A,
            "weight_strategic_relevance": w_R,
            "weight_evidence_strength": w_ES,
            "weight_effort": w_E,
        }

        if new_weights != current_weights:
            db.save_setting("prioritization_weights", new_weights)

    # 2. Retrieve or derive opportunities
    items = db.get_opportunities()
    if not items:
        # Auto-derive from reviews if not already populated
        df = db.get_reviews_df(app_identifier=selected_app_id)
        items = derive_opportunities_from_reviews(df, weights=new_weights)
        db.save_opportunities(items)
    else:
        # Recalculate with currently tuned weights
        items = recalculate_items(items, weights=new_weights)
        db.save_opportunities(items)

    if not items:
        st.info("No opportunity items to score. Ingest review data to generate candidates.")
        return

    # 3. Export Roadmap Button & Summary
    top_col1, top_col2 = st.columns([8, 4])
    with top_col1:
        st.markdown(f"**{len(items)} Prioritized Opportunities** ranked by computed return on investment:")
    with top_col2:
        export_data = pd.DataFrame([{
            "Rank": idx + 1,
            "Title": it.title,
            "Category": it.category,
            "Priority Score": it.priority_score,
            "Frequency": it.frequency,
            "Severity": it.severity,
            "Affected Users": it.affected_users,
            "Strategic Relevance": it.strategic_relevance,
            "Implementation Effort": it.implementation_effort,
            "Evidence Strength": it.evidence_strength,
            "Confidence": it.confidence_multiplier,
            "Proposed Action": it.proposed_action,
            "Strategic Category": it.strategic_category,
        } for idx, it in enumerate(items)])

        st.download_button(
            "📥 Export Prioritization Roadmap",
            data=export_data.to_csv(index=False),
            file_name="prioritized_opportunity_roadmap.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # 4. Detailed Ranked Cards with Math Breakdown
    for idx, item in enumerate(items):
        rank = idx + 1
        breakdown = item.score_breakdown
        raw_score = item.priority_score
        norm_score = breakdown.get("normalized_score_100", 50.0)

        st.markdown(f"""
        <div class="radar-card" style="border-left: 4px solid {'#10b981' if rank == 1 else ('#00f2fe' if rank == 2 else '#64748b')};">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-weight: 800; font-size: 1.1rem; color: #00f2fe;">#{rank}</span>
                        <span class="badge" style="background: rgba(255,255,255,0.08); color: #e2e8f0;">{item.category}</span>
                        <span class="badge" style="background: rgba(0, 242, 254, 0.15); color: #00f2fe;">{item.strategic_category}</span>
                    </div>
                    <h3 style="margin: 8px 0 4px 0; color: #ffffff; font-size: 1.15rem; font-weight: 700;">
                        {item.title}
                    </h3>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 0.72rem; color: #94a3b8; text-transform: uppercase;">Priority Score</div>
                    <div style="font-size: 1.6rem; font-weight: 800; color: #00f2fe;">{raw_score:.2f}</div>
                    <div style="font-size: 0.75rem; color: #10b981;">{norm_score:.0f}/100 Index</div>
                </div>
            </div>

            <p style="color: #cbd5e1; font-size: 0.90rem; line-height: 1.5; margin: 8px 0 12px 0;">
                {item.description}
            </p>

            <div style="background: rgba(0,0,0,0.25); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 10px 14px; margin-bottom: 12px;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; margin-bottom: 6px;">
                    📐 Mathematical Factor Breakdown
                </div>
                <div style="display: grid; grid-template-columns: repeat(6, 1fr); gap: 8px; text-align: center;">
                    <div><span style="font-size: 0.70rem; color: #64748b;">Freq (F)</span><br><strong style="color: #ffffff;">{item.frequency}/5</strong></div>
                    <div><span style="font-size: 0.70rem; color: #64748b;">Severity (S)</span><br><strong style="color: #ef4444;">{item.severity}/5</strong></div>
                    <div><span style="font-size: 0.70rem; color: #64748b;">Users (A)</span><br><strong style="color: #ffffff;">{item.affected_users}/5</strong></div>
                    <div><span style="font-size: 0.70rem; color: #64748b;">Strategy (R)</span><br><strong style="color: #00f2fe;">{item.strategic_relevance}/5</strong></div>
                    <div><span style="font-size: 0.70rem; color: #64748b;">Evidence (ES)</span><br><strong style="color: #ffffff;">{item.evidence_strength}/5</strong></div>
                    <div><span style="font-size: 0.70rem; color: #64748b;">Effort (E)</span><br><strong style="color: #f59e0b;">{item.implementation_effort}/5</strong></div>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 8px;">
                <div style="background: rgba(0, 242, 254, 0.05); border: 1px solid rgba(0, 242, 254, 0.2); border-radius: 6px; padding: 8px 12px;">
                    <div style="font-size: 0.74rem; font-weight: 700; color: #00f2fe; text-transform: uppercase;">Proposed Action</div>
                    <div style="color: #e2e8f0; font-size: 0.84rem; margin-top: 2px;">{item.proposed_action}</div>
                </div>
                <div style="background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 6px; padding: 8px 12px;">
                    <div style="font-size: 0.74rem; font-weight: 700; color: #34d399; text-transform: uppercase;">Engineering Next Step</div>
                    <div style="color: #a7f3d0; font-size: 0.84rem; margin-top: 2px;">{item.recommended_next_step}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander(f"🔍 Inspect Mathematical Formula & Evidence for #{rank}"):
            st.markdown(f"**Formula string:** `{breakdown.get('formula_display', 'N/A')}`")
            st.markdown(f"- **Weighted Impact Numerator:** `{breakdown.get('numerator', 0)}`")
            st.markdown(f"- **Weighted Effort Denominator:** `{breakdown.get('denominator', 0)}`")
            st.markdown(f"- **Confidence Multiplier:** `{item.confidence_multiplier}`")
            st.markdown(f"- **Risk / Limitation:** *{item.risk_or_limitation}*")
            if item.supporting_quotes:
                st.markdown("**Supporting Review Quotes:**")
                for q in item.supporting_quotes:
                    st.markdown(f"> *\"{q}\"*")
