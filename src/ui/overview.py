"""
src/ui/overview.py
Section 1: Executive Overview.
High-level KPI dashboard, active portfolio health, rating trajectory, and executive briefing.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.database import DatabaseManager
from src.ai_analyzer import AIAnalyzerEngine


def render_overview(db: DatabaseManager, selected_app_id: str):
    st.markdown("## 📊 Executive Overview")
    st.markdown(
        "<p style='color: #94a3b8; font-size: 0.95rem; margin-top: -10px;'>"
        "High-level portfolio health, rating trajectories, and top retention risks."
        "</p>",
        unsafe_allow_html=True
    )

    df = db.get_reviews_df(app_identifier=selected_app_id)

    if df.empty:
        st.warning("⚠️ No review records found in database. Ingest a dataset in **Data Import & Management** to begin.")
        return

    # Check synthetic state
    is_synth_dataset = df["is_synthetic"].any()
    if is_synth_dataset:
        st.markdown(
            """
            <div style="background: rgba(251, 146, 60, 0.1); border: 1px dashed rgba(251, 146, 60, 0.4); 
                        border-radius: 8px; padding: 10px 16px; margin-bottom: 20px; display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.1rem;">🧪</span>
                <span style="color: #fb923c; font-size: 0.85rem; font-weight: 600;">
                    SYNTHETIC DEMO DATASET ACTIVE: All metrics shown reflect synthetic benchmark data generated for development testing.
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 1. Headline KPIs
    total_reviews = len(df)
    avg_rating = df["rating"].mean()
    neg_reviews = len(df[df["rating"] <= 2])
    neg_pct = (neg_reviews / total_reviews) * 100
    pos_reviews = len(df[df["rating"] >= 4])
    pos_pct = (pos_reviews / total_reviews) * 100

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-label">Total Reviews Analyzed</div>
            <div class="kpi-value">{total_reviews:,}</div>
            <div class="kpi-subtext">{'100% Synthetic' if is_synth_dataset else 'Verified Store Ingest'}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        rating_color = "#10b981" if avg_rating >= 4.0 else ("#f59e0b" if avg_rating >= 3.0 else "#ef4444")
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-label">Average Store Rating</div>
            <div class="kpi-value" style="color: {rating_color};">{avg_rating:.2f} ★</div>
            <div class="kpi-subtext">Out of 5.0 store scale</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-label">Critical Rating Drag</div>
            <div class="kpi-value" style="color: #ef4444;">{neg_pct:.1f}%</div>
            <div class="kpi-subtext">{neg_reviews:,} reviews at 1★ or 2★</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-label">Positive Sentiment</div>
            <div class="kpi-value" style="color: #10b981;">{pos_pct:.1f}%</div>
            <div class="kpi-subtext">{pos_reviews:,} reviews at 4★ or 5★</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)

    # 2. Executive Synthesis Card
    analyzer = AIAnalyzerEngine()
    brief = analyzer.generate_executive_brief(df, app_name=df.iloc[0]["app_name"])

    st.markdown(f"""
    <div class="radar-card" style="border-left: 4px solid #00f2fe;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <div style="font-weight: 700; font-size: 1.05rem; color: #ffffff;">{brief['headline']}</div>
            <span class="badge" style="background: rgba(0, 242, 254, 0.15); color: #00f2fe; border: 1px solid rgba(0, 242, 254, 0.4);">
                Health: {brief['health_status']}
            </span>
        </div>
        <div style="color: #cbd5e1; font-size: 0.92rem; line-height: 1.6;">
            {brief['summary']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. Charts: Trajectory and Category Split
    c_left, c_right = st.columns([6, 4])

    with c_left:
        st.markdown("#### 📈 Rating Trajectory & Volume Over Time")
        # Aggregate by review_date
        daily = df.groupby("review_date").agg(
            avg_rating=("rating", "mean"),
            volume=("review_id", "count")
        ).reset_index().sort_values("review_date")
        
        # 7-day rolling average
        daily["rolling_avg"] = daily["avg_rating"].rolling(window=7, min_periods=1).mean()

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=daily["review_date"],
            y=daily["volume"],
            name="Daily Reviews",
            marker_color="rgba(255, 255, 255, 0.12)",
            yaxis="y2"
        ))
        fig.add_trace(go.Scatter(
            x=daily["review_date"],
            y=daily["rolling_avg"],
            name="7-Day Rolling Rating",
            line=dict(color="#00f2fe", width=3),
            mode="lines"
        ))

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=20, b=0),
            height=320,
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(showgrid=False, color="#94a3b8"),
            yaxis=dict(
                title="Avg Rating",
                range=[1, 5.2],
                showgrid=True,
                gridcolor="rgba(255,255,255,0.05)",
                color="#94a3b8"
            ),
            yaxis2=dict(
                title="Review Count",
                overlaying="y",
                side="right",
                showgrid=False,
                color="#64748b"
            ),
        )
        st.plotly_chart(fig, use_container_width=True)

    with c_right:
        st.markdown("#### 🎯 Feedback Category Breakdown")
        cat_counts = df["effective_category"].value_counts().reset_index()
        cat_counts.columns = ["category", "count"]

        color_map = {
            "Bugs and crashes": "#ef4444",
            "Performance": "#f59e0b",
            "User interface and usability": "#3b82f6",
            "Advertising and monetization": "#ec4899",
            "Missing features": "#8b5cf6",
            "Account and onboarding": "#06b6d4",
            "Pricing and subscriptions": "#eab308",
            "Positive feedback": "#10b981",
            "Other": "#94a3b8",
        }

        fig_pie = px.pie(
            cat_counts,
            values="count",
            names="category",
            color="category",
            color_discrete_map=color_map,
            hole=0.55,
        )
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0),
            height=320,
            showlegend=False,
        )
        fig_pie.update_traces(
            textposition="inside",
            textinfo="percent+label",
            marker=dict(line=dict(color="#08090d", width=2))
        )
        st.plotly_chart(fig_pie, use_container_width=True)
