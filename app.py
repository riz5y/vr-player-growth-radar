"""
app.py
App Opportunity Radar — Mobile App Growth & Product Intelligence Platform.
Entry point for the Streamlit web application.
"""

import streamlit as st
from pathlib import Path

# Streamlit Page Config MUST be the first Streamlit command
st.set_page_config(
    page_title="App Opportunity Radar",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.database import DatabaseManager
from src.importer import ReviewImporter
from src.models import CompetitorApp
from src.scoring import derive_opportunities_from_reviews
from src.ui.styles import inject_custom_css
from src.ui.overview import render_overview
from src.ui.reviews_view import render_reviews_view
from src.ui.insights_view import render_insights_view
from src.ui.competitors_view import render_competitors_view
from src.ui.prioritization_view import render_prioritization_view
from src.ui.importer_view import render_importer_view
from src.ui.settings_view import render_settings_view

# Initialize database
db = DatabaseManager()

# Auto-seed if first time running and reviews table is empty
stats = db.get_database_stats()
if stats["total_reviews"] == 0:
    sample_reviews_path = Path(__file__).resolve().parent / "data" / "sample_reviews.csv"
    if sample_reviews_path.exists():
        res = ReviewImporter.import_from_csv(str(sample_reviews_path), force_synthetic_flag=True)
        db.save_reviews(res.valid_records)

    sample_comps_path = Path(__file__).resolve().parent / "data" / "sample_competitors.csv"
    if sample_comps_path.exists():
        import pandas as pd
        comp_df = pd.read_csv(sample_comps_path)
        comps = []
        for _, row in comp_df.iterrows():
            comps.append(CompetitorApp(
                competitor_id=str(row['competitor_id']),
                app_name=str(row['app_name']),
                app_identifier=str(row['app_identifier']),
                rating=float(row['rating']),
                total_reviews=int(row['total_reviews']),
                primary_category=str(row['primary_category']),
                strengths=[s.strip() for s in str(row['strengths']).split('|') if s.strip()],
                weaknesses=[w.strip() for w in str(row['weaknesses']).split('|') if w.strip()],
                praised_features=[p.strip() for p in str(row['praised_features']).split('|') if p.strip()],
                positioning_summary=str(row.get('positioning_summary', '')),
                is_synthetic=True,
            ))
        db.save_competitors(comps)

    df_init = db.get_reviews_df()
    opps = derive_opportunities_from_reviews(df_init)
    db.save_opportunities(opps)

# Inject styling
inject_custom_css()

# -------------------------------------------------------------
# Sidebar Navigation & App Selector
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 14px;">
        <div style="font-size: 1.8rem;">⚡</div>
        <div>
            <div style="font-weight: 800; font-size: 1.15rem; color: #ffffff; letter-spacing: -0.02em;">
                Opportunity Radar
            </div>
            <div style="font-size: 0.72rem; color: #00f2fe; text-transform: uppercase; font-weight: 600;">
                Mobile Product Intelligence
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # App Selector
    apps_list = db.get_distinct_apps()
    if apps_list:
        app_names = [a["app_identifier"] for a in apps_list]
        selected_app_id = st.selectbox("Active App Target", app_names, index=0)
    else:
        selected_app_id = "com.vrplayer.vrvideoplayer.videos360.vrvideos.vrapp"
        st.caption(f"Target: `{selected_app_id}`")

    st.markdown("---")

    # 7-Section Navigation Menu
    nav_selection = st.radio(
        "Navigation",
        [
            "📊 Executive Overview",
            "🔍 Review Intelligence",
            "🧠 AI Insights & Recs",
            "🥊 Competitor Intelligence",
            "🎯 Opportunity Prioritization",
            "📥 Data Import & Management",
            "⚙️ Settings & Data Sources",
        ],
        index=0,
    )

    st.markdown("---")

    # Footer metrics
    db_stats = db.get_database_stats()
    st.markdown(f"""
    <div style="font-size: 0.75rem; color: #64748b; line-height: 1.5;">
        <div>Database: <strong style="color: #94a3b8;">SQLite (Local)</strong></div>
        <div>Indexed Reviews: <strong style="color: #94a3b8;">{db_stats['total_reviews']:,}</strong></div>
        <div>Mode: <strong style="color: #10b981;">Zero-Cost / Offline</strong></div>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------
# Main View Router
# -------------------------------------------------------------
if "Executive Overview" in nav_selection:
    render_overview(db, selected_app_id)
elif "Review Intelligence" in nav_selection:
    render_reviews_view(db, selected_app_id)
elif "AI Insights & Recs" in nav_selection:
    render_insights_view(db, selected_app_id)
elif "Competitor Intelligence" in nav_selection:
    render_competitors_view(db, selected_app_id)
elif "Opportunity Prioritization" in nav_selection:
    render_prioritization_view(db, selected_app_id)
elif "Data Import & Management" in nav_selection:
    render_importer_view(db, selected_app_id)
elif "Settings & Data Sources" in nav_selection:
    render_settings_view(db)
