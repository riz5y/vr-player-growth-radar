"""
src/ui/competitors_view.py
Section 4: Competitor Intelligence.
Comparative benchmarking, feature gap analysis, and differentiation opportunities.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from src.database import DatabaseManager


def render_competitors_view(db: DatabaseManager, selected_app_id: str):
    st.markdown("## 🥊 Competitor Intelligence & Benchmarking")
    st.markdown(
        "<p style='color: #94a3b8; font-size: 0.95rem; margin-top: -10px;'>"
        "Study market positioning, identify competitor weaknesses, and find product differentiation gaps."
        "</p>",
        unsafe_allow_html=True
    )

    competitors = db.get_competitors()
    our_df = db.get_reviews_df(app_identifier=selected_app_id)
    our_rating = our_df["rating"].mean() if not our_df.empty else 0.0
    our_reviews = len(our_df)

    if not competitors:
        st.info("No competitor benchmark data present. Load competitor samples in **Data Import & Management**.")
        return

    # 1. High-level comparative chart
    st.markdown("#### 📊 Store Rating vs. Review Volume Comparison")
    comp_rows = [{
        "App": "Our App (VR 360 Player)",
        "Rating": round(our_rating, 2),
        "Reviews": our_reviews,
        "Type": "Internal App"
    }]
    for c in competitors:
        comp_rows.append({
            "App": c.app_name,
            "Rating": c.rating,
            "Reviews": c.total_reviews,
            "Type": "Competitor"
        })

    c_df = pd.DataFrame(comp_rows)

    c_left, c_right = st.columns([6, 6])
    with c_left:
        fig_r = px.bar(
            c_df,
            x="App",
            y="Rating",
            color="Type",
            color_discrete_map={"Internal App": "#00f2fe", "Competitor": "#64748b"},
            text="Rating"
        )
        fig_r.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=280,
            margin=dict(l=0, r=0, t=10, b=0),
            yaxis=dict(range=[0, 5.2], color="#94a3b8", gridcolor="rgba(255,255,255,0.05)"),
            xaxis=dict(color="#94a3b8"),
            showlegend=False,
        )
        st.plotly_chart(fig_r, use_container_width=True)

    with c_right:
        fig_v = px.bar(
            c_df,
            x="App",
            y="Reviews",
            color="Type",
            color_discrete_map={"Internal App": "#00f2fe", "Competitor": "#64748b"},
            text="Reviews"
        )
        fig_v.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=280,
            margin=dict(l=0, r=0, t=10, b=0),
            yaxis=dict(color="#94a3b8", gridcolor="rgba(255,255,255,0.05)"),
            xaxis=dict(color="#94a3b8"),
            showlegend=False,
        )
        st.plotly_chart(fig_v, use_container_width=True)

    st.markdown("---")

    # 2. Competitor Deep-Dive Cards
    st.markdown("#### 🔍 Competitor Feature Profiles & Positioning")

    for c in competitors:
        st.markdown(f"""
        <div class="radar-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div>
                    <h3 style="margin: 0; color: #ffffff; font-size: 1.15rem; font-weight: 700;">{c.app_name}</h3>
                    <span style="font-family: monospace; font-size: 0.78rem; color: #00f2fe;">{c.app_identifier}</span>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.35rem; font-weight: 800; color: #10b981;">{c.rating:.1f} ★</div>
                    <div style="font-size: 0.75rem; color: #94a3b8;">{c.total_reviews:,} store reviews</div>
                </div>
            </div>

            <p style="color: #cbd5e1; font-size: 0.90rem; margin-bottom: 12px; font-style: italic;">
                "{c.positioning_summary}"
            </p>

            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px;">
                <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 6px; padding: 10px;">
                    <div style="font-size: 0.75rem; font-weight: 700; color: #34d399; text-transform: uppercase;">✨ Praised Features</div>
                    <ul style="margin: 6px 0 0 16px; padding: 0; font-size: 0.82rem; color: #a7f3d0;">
                        {''.join(f'<li>{p}</li>' for p in c.praised_features)}
                    </ul>
                </div>

                <div style="background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 6px; padding: 10px;">
                    <div style="font-size: 0.75rem; font-weight: 700; color: #60a5fa; text-transform: uppercase;">💪 Core Strengths</div>
                    <ul style="margin: 6px 0 0 16px; padding: 0; font-size: 0.82rem; color: #bfdbfe;">
                        {''.join(f'<li>{s}</li>' for s in c.strengths)}
                    </ul>
                </div>

                <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 6px; padding: 10px;">
                    <div style="font-size: 0.75rem; font-weight: 700; color: #f87171; text-transform: uppercase;">⚡ Vulnerabilities / Complaints</div>
                    <ul style="margin: 6px 0 0 16px; padding: 0; font-size: 0.82rem; color: #fca5a5;">
                        {''.join(f'<li>{w}</li>' for w in c.weaknesses)}
                    </ul>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 3. Strategic Feature Gap Matrix
    st.markdown("#### 🎯 Market Opportunity Matrix")
    st.markdown("""
    | Market Opportunity | Competitor Status | Our Strategic Move | Impact |
    | :--- | :--- | :--- | :--- |
    | **Subtitles (.SRT/.VTT) in VR** | Only 1 competitor supports sidecar subtitles. | Build automatic local subtitle detection. | **High** (Capture international users) |
    | **Unintrusive VR Monetization** | All competitors spam ads or charge high subscriptions. | Implement session frequency capping during VR mode. | **Critical** (Curb 1★ rating drag) |
    | **Hardware Decoding Reliability** | Competitors experience audio desync on 4K MKV files. | Deploy ExoPlayer software fallback pipeline. | **High** (Defensive stability) |
    | **Instant Recenter Button** | Gyroscope drift is universally complained across all apps. | First to ship volume-button hardware recenter. | **Fast Win** (Differentiator) |
    """)
