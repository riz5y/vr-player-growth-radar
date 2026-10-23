import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import importlib
import data_manager
importlib.reload(data_manager)

from data_manager import (
    fetch_live_reviews,
    generate_demo_reviews,
    generate_ai_recommendations,
    get_app_metadata,
    get_fallback_app_metadata,
    CATEGORY_KEYWORDS
)

# Page configuration
st.set_page_config(
    page_title="GrowthRadar | Mobile App Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# ULTRA-ELITE MINIMALIST MODERN CSS (Linear / Vercel Aesthetic)
# ==========================================
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">

<style>
    /* Global Resets & Typography */
    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: #07090E !important;
        color: #F1F5F9 !important;
        letter-spacing: -0.011em;
    }

    /* Ambient background gradient glow */
    .stApp {
        background: radial-gradient(circle at 50% 0%, rgba(30, 58, 138, 0.15) 0%, rgba(7, 9, 14, 1) 60%) !important;
    }

    /* Remove default Streamlit top padding */
    .block-container {
        padding-top: 1.8rem !important;
        padding-bottom: 3.5rem !important;
        max-width: 1400px !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0B0E17 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.06) !important;
    }

    /* Hero App Banner */
    .app-hero-card {
        background: linear-gradient(135deg, rgba(17, 24, 39, 0.85) 0%, rgba(11, 15, 26, 0.95) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px 28px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(16px);
        margin-bottom: 24px;
        transition: border-color 0.3s ease;
    }
    .app-hero-card:hover {
        border-color: rgba(99, 102, 241, 0.3);
    }
    .app-icon {
        width: 76px;
        height: 76px;
        border-radius: 18px;
        object-fit: cover;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .app-meta-title {
        font-size: 1.55rem;
        font-weight: 700;
        letter-spacing: -0.025em;
        color: #FFFFFF;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .app-meta-sub {
        font-size: 0.88rem;
        color: #94A3B8;
        margin-top: 4px;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    /* Pulsing Status Dot */
    .live-dot {
        width: 8px;
        height: 8px;
        background-color: #10B981;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
        animation: pulse-green 2s infinite;
    }
    .demo-dot {
        width: 8px;
        height: 8px;
        background-color: #6366F1;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.7);
        animation: pulse-blue 2s infinite;
    }
    @keyframes pulse-green {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
    @keyframes pulse-blue {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(99, 102, 241, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(99, 102, 241, 0); }
    }

    /* Executive KPI Cards (Vercel Style) */
    .kpi-card {
        background: linear-gradient(180deg, rgba(20, 27, 44, 0.7) 0%, rgba(13, 17, 28, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 14px;
        padding: 20px 22px;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(12px);
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.35);
        box-shadow: 0 12px 28px -10px rgba(0, 0, 0, 0.5);
    }
    .kpi-label {
        font-size: 0.74rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #94A3B8;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .kpi-number {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        color: #F8FAFC;
        margin: 10px 0 4px 0;
    }
    .kpi-subtext {
        font-size: 0.80rem;
        font-weight: 500;
        color: #64748B;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .trend-up { color: #10B981; font-weight: 600; }
    .trend-down { color: #F43F5E; font-weight: 600; }
    .trend-neutral { color: #38BDF8; font-weight: 600; }

    /* Modern Pill Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: rgba(15, 23, 42, 0.6) !important;
        padding: 6px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        margin-bottom: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 38px;
        border-radius: 8px !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: #94A3B8 !important;
        border: none !important;
        padding: 0 18px !important;
        transition: all 0.2s ease !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35) !important;
    }

    /* Raycast / Linear Style Experiment Cards */
    .ticket-card {
        background: rgba(17, 24, 39, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 14px;
        transition: all 0.2s ease;
    }
    .ticket-card:hover {
        background: rgba(22, 30, 49, 0.85);
        border-color: rgba(255, 255, 255, 0.12);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
    }
    .pill {
        display: inline-flex;
        align-items: center;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.02em;
    }
    .pill-p0 { background: rgba(239, 68, 68, 0.15); color: #FCA5A5; border: 1px solid rgba(239, 68, 68, 0.3); }
    .pill-p1 { background: rgba(245, 158, 11, 0.15); color: #FCD34D; border: 1px solid rgba(245, 158, 11, 0.3); }
    .pill-p2 { background: rgba(16, 185, 129, 0.15); color: #6EE7B7; border: 1px solid rgba(16, 185, 129, 0.3); }
    .pill-cat { background: rgba(99, 102, 241, 0.15); color: #A5B4FC; border: 1px solid rgba(99, 102, 241, 0.25); }
    .pill-owner { background: rgba(148, 163, 184, 0.12); color: #CBD5E1; border: 1px solid rgba(148, 163, 184, 0.2); }

    .quote-card {
        background-color: rgba(9, 13, 22, 0.6);
        border-left: 3px solid #6366F1;
        padding: 8px 14px;
        border-radius: 0 8px 8px 0;
        margin: 6px 0;
        font-size: 0.85rem;
        color: #CBD5E1;
        font-style: italic;
    }

    /* Sleek buttons */
    .stButton>button {
        border-radius: 9px !important;
        font-weight: 600 !important;
        font-size: 0.84rem !important;
        transition: all 0.2s ease !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.4);
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# STATE MANAGEMENT
# ==========================================
if 'reviews_df' not in st.session_state:
    st.session_state.reviews_df = generate_demo_reviews("Pulse Player Pro", count=250)
if 'package_id' not in st.session_state:
    st.session_state.package_id = "org.videolan.vlc"
if 'app_info' not in st.session_state:
    st.session_state.app_info = get_fallback_app_metadata("Pulse Player Pro")
if 'is_live' not in st.session_state:
    st.session_state.is_live = False


# ==========================================
# SIDEBAR CONTROLS
# ==========================================
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 14px;">
        <div style="background: linear-gradient(135deg, #3B82F6 0%, #6366F1 100%); width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.1rem;">
            ⚡
        </div>
        <div>
            <div style="font-size: 1.05rem; font-weight: 700; color: #FFFFFF; letter-spacing: -0.02em;">GrowthRadar</div>
            <div style="font-size: 0.72rem; color: #64748B; font-weight: 600;">ENTERPRISE INTELLIGENCE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    mode = st.radio(
        "Ingestion Source",
        ["📊 Sample Demo App", "🌐 Live Google Play Ingestion"],
        index=0 if not st.session_state.is_live else 1,
        label_visibility="collapsed"
    )

    if mode == "📊 Sample Demo App":
        if st.session_state.is_live or st.session_state.reviews_df.empty:
            st.session_state.reviews_df = generate_demo_reviews("Pulse Player Pro", count=250)
            st.session_state.app_info = get_fallback_app_metadata("Pulse Player Pro")
            st.session_state.is_live = False
            st.rerun()

    else:
        st.markdown("<p style='font-size: 0.78rem; font-weight: 600; color: #94A3B8; margin-top: 10px; margin-bottom: 4px;'>TARGET PLAY STORE APP</p>", unsafe_allow_html=True)
        package_input = st.text_input(
            "Package ID",
            value=st.session_state.package_id,
            placeholder="e.g. org.videolan.vlc",
            label_visibility="collapsed"
        )

        st.caption("Benchmark Presets:")
        cp1, cp2, cp3 = st.columns(3)
        if cp1.button("VLC", use_container_width=True):
            package_input = "org.videolan.vlc"
        if cp2.button("Spotify", use_container_width=True):
            package_input = "com.spotify.music"
        if cp3.button("Duolingo", use_container_width=True):
            package_input = "com.duolingo"

        st.markdown("<p style='font-size: 0.78rem; font-weight: 600; color: #94A3B8; margin-top: 10px; margin-bottom: 2px;'>FETCH CONFIGURATION</p>", unsafe_allow_html=True)
        fetch_count = st.slider("Max Reviews", min_value=50, max_value=300, value=150, step=50)
        country_code = st.selectbox("Storefront Country", ["us", "gb", "in", "de", "ca"], index=0)

        if st.button("🚀 Analyze Play Store App", type="primary", use_container_width=True):
            with st.spinner(f"Ingesting metadata & reviews for '{package_input}'..."):
                metadata = get_app_metadata(package_input)
                live_df, err = fetch_live_reviews(package_input, count=fetch_count, country=country_code)
                if err:
                    st.error(err)
                else:
                    st.session_state.reviews_df = live_df
                    st.session_state.package_id = package_input
                    st.session_state.app_info = metadata
                    st.session_state.is_live = True
                    st.rerun()

    st.markdown("---")
    st.markdown("<p style='font-size: 0.78rem; font-weight: 600; color: #94A3B8; margin-bottom: 6px;'>FILTERS & SLICING</p>", unsafe_allow_html=True)
    
    selected_scores = st.multiselect("Star Ratings", [1, 2, 3, 4, 5], default=[1, 2, 3, 4, 5])
    all_categories = list(CATEGORY_KEYWORDS.keys()) + ["Praise / General"]
    selected_categories = st.multiselect("Complaint Themes", all_categories, default=all_categories)
    selected_sentiments = st.multiselect("Sentiment", ["Positive", "Neutral", "Negative"], default=["Positive", "Neutral", "Negative"])
    search_query = st.text_input("Search Text", placeholder="filter keywords...", label_visibility="collapsed")


# ==========================================
# FILTER REVIEWS
# ==========================================
df_raw = st.session_state.reviews_df
df = df_raw.copy()

if not df.empty:
    if selected_scores:
        df = df[df['score'].isin(selected_scores)]
    if selected_categories:
        df = df[df['category'].isin(selected_categories)]
    if selected_sentiments:
        df = df[df['sentiment'].isin(selected_sentiments)]
    if search_query:
        df = df[df['content'].str.contains(search_query, case=False, na=False)]


# ==========================================
# HERO APP HEADER (Silicon Valley Quality)
# ==========================================
info = st.session_state.app_info
score_stars = "★" * int(round(info.get('score', 4.0)))

status_pill = f"""
<div style="display: flex; align-items: center; gap: 8px; background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.3); padding: 5px 14px; border-radius: 24px;">
    <span class="live-dot"></span>
    <span style="font-size: 0.74rem; font-weight: 700; color: #10B981; letter-spacing: 0.05em; font-family: 'JetBrains Mono', monospace;">LIVE PLAY SYNC</span>
</div>
""" if st.session_state.is_live else f"""
<div style="display: flex; align-items: center; gap: 8px; background: rgba(99, 102, 241, 0.12); border: 1px solid rgba(99, 102, 241, 0.3); padding: 5px 14px; border-radius: 24px;">
    <span class="demo-dot"></span>
    <span style="font-size: 0.74rem; font-weight: 700; color: #818CF8; letter-spacing: 0.05em; font-family: 'JetBrains Mono', monospace;">BENCHMARK PROTOTYPE</span>
</div>
"""

st.markdown(f"""
<div class="app-hero-card">
    <div style="display: flex; align-items: center; gap: 20px;">
        <img class="app-icon" src="{info.get('icon')}" alt="App Icon"/>
        <div>
            <div class="app-meta-title">
                {info.get('title')}
                <span style="font-size: 0.72rem; font-weight: 600; background: rgba(255,255,255,0.08); padding: 2px 8px; border-radius: 5px; color: #94A3B8;">{info.get('genre')}</span>
            </div>
            <div class="app-meta-sub">
                <span>By <strong style="color: #E2E8F0;">{info.get('developer')}</strong></span>
                <span>•</span>
                <span style="color: #FBBF24;">{score_stars} <strong style="color: #FFFFFF;">{info.get('score')}</strong>/5.0</span>
                <span>•</span>
                <span>{info.get('installs')} installs</span>
            </div>
        </div>
    </div>
    <div>
        {status_pill}
    </div>
</div>
""", unsafe_allow_html=True)


# ==========================================
# EXECUTIVE METRICS STRIP
# ==========================================
if not df.empty:
    total_revs = len(df)
    avg_rating = round(df['score'].mean(), 2)
    pos_count = len(df[df['sentiment'] == 'Positive'])
    neg_count = len(df[df['sentiment'] == 'Negative'])
    net_sentiment = round(((pos_count - neg_count) / total_revs) * 100, 1) if total_revs > 0 else 0
    crash_count = len(df[df['category'] == 'Critical Bug / Crash'])
    crash_pct = round((crash_count / total_revs) * 100, 1) if total_revs > 0 else 0

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label"><span>Sample Size</span> <span>📊</span></div>
            <div class="kpi-number">{total_revs:,}</div>
            <div class="kpi-subtext"><span class="trend-neutral">●</span> Current Filter Slice</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        r_color = "trend-up" if avg_rating >= 4.0 else ("trend-down" if avg_rating < 3.2 else "trend-neutral")
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label"><span>Review Sentiment Score</span> <span>⭐</span></div>
            <div class="kpi-number">{avg_rating} <span style="font-size: 1.1rem; color: #FBBF24;">★</span></div>
            <div class="kpi-subtext"><span class="{r_color}">●</span> Target: 4.3★ healthy bar</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        s_color = "trend-up" if net_sentiment > 15 else ("trend-down" if net_sentiment < 0 else "trend-neutral")
        sign = "+" if net_sentiment > 0 else ""
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label"><span>Net Sentiment Index</span> <span>💬</span></div>
            <div class="kpi-number">{sign}{net_sentiment}%</div>
            <div class="kpi-subtext"><span class="{s_color}">●</span> {pos_count} Pos vs {neg_count} Neg</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        cr_color = "trend-down" if crash_pct > 12 else "trend-up"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label"><span>Critical Defect Rate</span> <span>🚨</span></div>
            <div class="kpi-number">{crash_pct}%</div>
            <div class="kpi-subtext"><span class="{cr_color}">●</span> {crash_count} Crash/Freeze mentions</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ==========================================
# MAIN TABBED INTERFACE
# ==========================================
tab_radar, tab_ai, tab_explorer, tab_deploy = st.tabs([
    "📊 Opportunity Radar", 
    "🎯 AI Growth Experiments", 
    "🔍 Granular Review Explorer", 
    "☁️ Cloud Architecture & Pitch"
])


# ----------------------------------------------------
# TAB 1: OPPORTUNITY RADAR
# ----------------------------------------------------
with tab_radar:
    if df.empty:
        st.info("No reviews match your selected filters. Please adjust the sidebar controls.")
    else:
        col_g1, col_g2 = st.columns([1, 1])

        # Modern palette
        dark_palette = ['#6366F1', '#EC4899', '#F59E0B', '#3B82F6', '#10B981', '#8B5CF6', '#14B8A6']

        with col_g1:
            st.markdown("##### 🧩 Problem & Opportunity Theme Distribution")
            cat_df = df['category'].value_counts().reset_index()
            cat_df.columns = ['Category', 'Reviews']

            fig_donut = px.pie(
                cat_df,
                names='Category',
                values='Reviews',
                hole=0.55,
                color_discrete_sequence=dark_palette
            )
            fig_donut.update_traces(
                textposition='inside',
                textinfo='percent+label',
                marker=dict(line=dict(color='#07090E', width=2))
            )
            fig_donut.update_layout(
                showlegend=False,
                margin=dict(t=10, b=10, l=10, r=10),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#CBD5E1", family="Plus Jakarta Sans"),
                height=320
            )
            st.plotly_chart(fig_donut, use_container_width=True)

        with col_g2:
            st.markdown("##### ⭐ Star Rating Composition by Theme")
            cross_df = pd.crosstab(df['category'], df['score']).reset_index()
            
            fig_stack = go.Figure()
            star_colors = {1: '#EF4444', 2: '#F97316', 3: '#FBBF24', 4: '#34D399', 5: '#10B981'}
            for star in sorted(df['score'].unique()):
                if star in cross_df.columns:
                    fig_stack.add_trace(go.Bar(
                        name=f"{star}★",
                        x=cross_df['category'],
                        y=cross_df[star],
                        marker_color=star_colors.get(star, '#94A3B8'),
                        marker_line=dict(color='#07090E', width=1)
                    ))
            fig_stack.update_layout(
                barmode='stack',
                margin=dict(t=10, b=10, l=10, r=10),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#CBD5E1", family="Plus Jakarta Sans"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=320,
                xaxis=dict(gridcolor='rgba(255,255,255,0.04)', tickangle=-20),
                yaxis=dict(gridcolor='rgba(255,255,255,0.06)')
            )
            st.plotly_chart(fig_stack, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_g3, col_g4 = st.columns([1, 1])

        with col_g3:
            st.markdown("##### 📈 Weekly Sentiment Trajectory")
            if 'date' in df.columns:
                trend = df.copy()
                trend['week'] = trend['date'].dt.to_period('W').dt.start_time
                weekly = trend.groupby('week')['sentiment_score'].mean().reset_index()
                
                fig_line = px.area(
                    weekly,
                    x='week',
                    y='sentiment_score',
                    labels={'week': 'Week', 'sentiment_score': 'Sentiment (-1.0 to +1.0)'}
                )
                fig_line.update_traces(
                    line_color='#6366F1',
                    fillcolor='rgba(99, 102, 241, 0.12)',
                    line_width=2.5
                )
                fig_line.add_hline(y=0.0, line_dash="dash", line_color="#475569")
                fig_line.update_layout(
                    margin=dict(t=10, b=10, l=10, r=10),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color="#CBD5E1", family="Plus Jakarta Sans"),
                    height=280,
                    xaxis=dict(gridcolor='rgba(255,255,255,0.04)'),
                    yaxis=dict(gridcolor='rgba(255,255,255,0.06)')
                )
                st.plotly_chart(fig_line, use_container_width=True)
            else:
                st.caption("Temporal series not available.")

        with col_g4:
            st.markdown("##### 📱 Churn Spikes by App Release Version")
            if 'version' in df.columns:
                neg_vers = df[df['score'] <= 2]['version'].value_counts().reset_index()
                neg_vers.columns = ['Version', 'Complaints']
                
                fig_vers = px.bar(
                    neg_vers.head(6),
                    x='Version',
                    y='Complaints',
                    color='Complaints',
                    color_continuous_scale=['#3B82F6', '#EF4444']
                )
                fig_vers.update_layout(
                    margin=dict(t=10, b=10, l=10, r=10),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color="#CBD5E1", family="Plus Jakarta Sans"),
                    coloraxis_showscale=False,
                    height=280,
                    xaxis=dict(gridcolor='rgba(255,255,255,0.04)'),
                    yaxis=dict(gridcolor='rgba(255,255,255,0.06)')
                )
                st.plotly_chart(fig_vers, use_container_width=True)


# ----------------------------------------------------
# TAB 2: AI GROWTH EXPERIMENTS (Raycast / Linear Style)
# ----------------------------------------------------
with tab_ai:
    st.markdown("#### 🎯 AI Opportunity Matrix & Experiment Backlog")
    st.caption("Ranked product and marketing interventions derived directly from recurring user friction.")

    recs = generate_ai_recommendations(df_raw)

    # 1. Interactive Impact vs Effort Quadrant Scatter Plot
    mat_rows = []
    for r in recs:
        mat_rows.append({
            "Experiment": r['title'],
            "Impact": r['impact_score'],
            "Effort": r['effort_score'],
            "Priority": r['priority']
        })
    mat_df = pd.DataFrame(mat_rows)

    fig_matrix = px.scatter(
        mat_df,
        x="Effort",
        y="Impact",
        text="Experiment",
        color="Priority",
        color_discrete_map={"P0 - Blocker": "#EF4444", "P1 - High": "#F59E0B", "P2 - Growth Lever": "#10B981"},
        range_x=[0.5, 9.5],
        range_y=[5.5, 10.5],
        labels={"Effort": "Engineering Effort Score (Lower = Faster)", "Impact": "Retention & Rating Impact"}
    )
    fig_matrix.add_vline(x=5.0, line_dash="dash", line_color="rgba(255,255,255,0.1)")
    fig_matrix.add_hline(y=7.8, line_dash="dash", line_color="rgba(255,255,255,0.1)")

    fig_matrix.add_annotation(x=2.5, y=10.2, text="🚀 QUICK WINS", showarrow=False, font=dict(color="#10B981", size=11, family="JetBrains Mono"))
    fig_matrix.add_annotation(x=7.5, y=10.2, text="🏆 STRATEGIC BETS", showarrow=False, font=dict(color="#60A5FA", size=11, family="JetBrains Mono"))
    fig_matrix.add_annotation(x=2.5, y=5.8, text="🔨 LOW-HANGING FILL-INS", showarrow=False, font=dict(color="#94A3B8", size=11, family="JetBrains Mono"))
    fig_matrix.add_annotation(x=7.5, y=5.8, text="⚠️ RE-EVALUATE", showarrow=False, font=dict(color="#EF4444", size=11, family="JetBrains Mono"))

    fig_matrix.update_traces(
        marker=dict(size=20, line=dict(width=1.5, color='#FFFFFF')),
        textposition='top center',
        textfont=dict(size=11, family="Plus Jakarta Sans", color="#F1F5F9")
    )
    fig_matrix.update_layout(
        paper_bgcolor='rgba(15, 23, 42, 0.4)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#CBD5E1", family="Plus Jakarta Sans"),
        height=360,
        margin=dict(t=20, b=20, l=10, r=10),
        xaxis=dict(gridcolor='rgba(255,255,255,0.04)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.06)')
    )
    st.plotly_chart(fig_matrix, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### 📋 Sprint-Ready Growth Tickets")

    for exp in recs:
        pill_priority = "pill-p0" if "P0" in exp['priority'] else ("pill-p1" if "P1" in exp['priority'] else "pill-p2")
        
        with st.expander(f"{exp['id']} • {exp['title']}", expanded=True if "P0" in exp['priority'] else False):
            st.markdown(f"""
            <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 12px; flex-wrap: wrap;">
                <span class="pill {pill_priority}">{exp['priority']}</span>
                <span class="pill pill-cat">{exp['category']}</span>
                <span class="pill pill-owner">Owner: {exp['action_owner']}</span>
                <span class="pill" style="background: rgba(168, 85, 247, 0.15); color: #D8B4FE; border: 1px solid rgba(168, 85, 247, 0.3);">Effort: {exp['effort_level']}</span>
                <span class="pill" style="background: rgba(14, 165, 233, 0.15); color: #7DD3FC; border: 1px solid rgba(14, 165, 233, 0.3);">Confidence: {exp.get('confidence', '90%')}</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"**Hypothesis & Solution:**")
            st.write(exp['hypothesis'])

            st.markdown(f"**Target Business Metric:**")
            st.markdown(f"`{exp['target_metric']}`")

            st.markdown(f"**User Verbatim Proof ({exp['evidence_count']} mentions):**")
            for q in exp['sample_quotes']:
                st.markdown(f"<div class='quote-card'>\"{q}\"</div>", unsafe_allow_html=True)

            st.download_button(
                label=f"📥 Export {exp['id']} as Jira / Linear Markdown",
                data=f"## [{exp['id']}] {exp['title']}\n**Priority:** {exp['priority']}\n**Target Metric:** {exp['target_metric']}\n\n### Hypothesis\n{exp['hypothesis']}\n\n### Verbatim User Evidence\n" + "\n".join(f"- \"{q}\"" for q in exp['sample_quotes']),
                file_name=f"{exp['id']}_linear_spec.md",
                mime="text/markdown",
                key=f"dl_btn_{exp['id']}"
            )


# ----------------------------------------------------
# TAB 3: GRANULAR REVIEW EXPLORER
# ----------------------------------------------------
with tab_explorer:
    st.markdown("#### 🔍 Filtered Review Feed")
    st.caption("Inspect raw user feedback, debug AI classification accuracy, and export targeted slices.")

    col_exp_1, col_exp_2 = st.columns([3, 1])
    with col_exp_2:
        csv_bytes = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export View to CSV",
            data=csv_bytes,
            file_name=f"export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    cols = ['score', 'category', 'sentiment', 'content', 'version', 'user_name', 'thumbs_up']
    view_df = df[[c for c in cols if c in df.columns]]

    st.dataframe(
        view_df,
        column_config={
            "score": st.column_config.NumberColumn("Rating", format="%d ★"),
            "category": st.column_config.TextColumn("Classification Theme"),
            "sentiment": st.column_config.TextColumn("Sentiment"),
            "content": st.column_config.TextColumn("Verbatim Feedback", width="large"),
            "version": st.column_config.TextColumn("App Ver"),
            "thumbs_up": st.column_config.NumberColumn("Helpful 👍")
        },
        use_container_width=True,
        height=480
    )


# ----------------------------------------------------
# TAB 4: CLOUD ARCHITECTURE & INTERNAL POSITIONING
# ----------------------------------------------------
with tab_deploy:
    st.markdown("#### ☁️ Production Cloud Deployment & Pitch Framework")
    st.caption("How this prototype operates as an automated 24/7 web application and how to present it.")

    col_d1, col_d2 = st.columns(2)

    with col_d1:
        st.markdown("""
        <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 20px;">
            <div style="font-weight: 700; color: #FFFFFF; font-size: 1.05rem; margin-bottom: 8px;">
                🚀 3-Minute Cloud Deployment (Free)
            </div>
            <p style="font-size: 0.85rem; color: #94A3B8;">
                Deploy this dashboard online so anyone on your team can open it via URL without installing Python.
            </p>
            <ol style="font-size: 0.85rem; color: #CBD5E1; padding-left: 20px; line-height: 1.7;">
                <li>Create a free repo on <strong style="color: #60A5FA;">GitHub</strong>.</li>
                <li>Push the code from this directory:
                    <pre style="background: #090D16; padding: 8px 12px; border-radius: 6px; font-size: 0.78rem; color: #38BDF8; margin-top: 6px;">git init
git add .
git commit -m "Growth Radar v1"
git push -u origin main</pre>
                </li>
                <li>Go to <a href="https://share.streamlit.io" target="_blank" style="color: #60A5FA;">share.streamlit.io</a>, connect your repository, and click <strong>Deploy</strong>.</li>
            </ol>
            <p style="font-size: 0.82rem; color: #10B981; font-weight: 600; margin-top: 8px;">
                ✔ Permanent URL (e.g. https://company-growth-radar.streamlit.app)
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_d2:
        st.markdown("""
        <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 20px;">
            <div style="font-weight: 700; color: #FFFFFF; font-size: 1.05rem; margin-bottom: 8px;">
                ⏱️ Automated Daily Cloud Scraping
            </div>
            <p style="font-size: 0.85rem; color: #94A3B8;">
                How to make it update continuously like commercial tools (App Radar, Sensor Tower):
            </p>
            <ul style="font-size: 0.85rem; color: #CBD5E1; padding-left: 20px; line-height: 1.7;">
                <li>The repo already includes <code>.github/workflows/daily_review_sync.yml</code>.</li>
                <li>It runs automatically every morning at 03:00 UTC using free GitHub Actions runner minutes.</li>
                <li>It scrapes new reviews, runs the classifier, and writes to a cloud database (like free-tier Supabase PostgreSQL).</li>
                <li>No local computer or server needs to remain powered on.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.5) 0%, rgba(15, 23, 42, 0.7) 100%); border: 1px solid rgba(99, 102, 241, 0.25); border-radius: 12px; padding: 22px;">
        <div style="font-weight: 700; color: #818CF8; font-size: 0.95rem; margin-bottom: 8px; letter-spacing: 0.05em; text-transform: uppercase;">
            💼 Recommended Manager Pitch (Word-for-Word)
        </div>
        <p style="font-style: italic; color: #E2E8F0; font-size: 0.92rem; line-height: 1.6; margin: 0;">
            "I built an internal prototype called <strong>GrowthRadar</strong> to help us translate user reviews and competitor signals directly into prioritized product experiments. It automatically categorizes feedback into crashes, paywall friction, and feature requests, then calculates an Impact vs. Effort matrix.<br><br>
            It is running 100% on public store data today so it required zero changes to our Android apps or backend. Here is the live link—if you find this valuable, we can test connecting it to our internal crash logs or analytics next."
        </p>
    </div>
    """, unsafe_allow_html=True)
