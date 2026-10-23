"""
src/ui/styles.py
Custom styling injection for App Opportunity Radar.
Delivers a high-contrast dark aesthetic with glassmorphic cards and elite typography.
"""

import streamlit as st


def inject_custom_css():
    """Injects custom CSS into the Streamlit app head."""
    custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    code, pre, .mono-text {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Main background */
    .stApp {
        background-color: #08090d;
        color: #f1f5f9;
    }

    /* Glass card containers */
    .radar-card {
        background: rgba(18, 22, 34, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 20px;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        margin-bottom: 16px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .radar-card:hover {
        border-color: rgba(0, 242, 254, 0.3);
    }

    /* Metric card */
    .kpi-container {
        background: linear-gradient(135deg, rgba(22, 27, 46, 0.9) 0%, rgba(13, 17, 28, 0.9) 100%);
        border: 1px solid rgba(255, 255, 255, 0.09);
        border-radius: 12px;
        padding: 16px 20px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .kpi-label {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #94a3b8;
        margin-bottom: 6px;
    }

    .kpi-value {
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #ffffff;
    }

    .kpi-subtext {
        font-size: 0.75rem;
        color: #64748b;
        margin-top: 4px;
    }

    /* Category Badges */
    .badge {
        display: inline-block;
        padding: 3px 10px;
        font-size: 0.72rem;
        font-weight: 600;
        border-radius: 9999px;
        letter-spacing: 0.02em;
        text-transform: uppercase;
    }

    .badge-bugs { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
    .badge-perf { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
    .badge-ui { background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
    .badge-ads { background: rgba(236, 72, 153, 0.15); color: #f472b6; border: 1px solid rgba(236, 72, 153, 0.3); }
    .badge-features { background: rgba(139, 92, 246, 0.15); color: #a78bfa; border: 1px solid rgba(139, 92, 246, 0.3); }
    .badge-positive { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-other { background: rgba(148, 163, 184, 0.15); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.3); }
    .badge-synthetic { background: rgba(251, 146, 60, 0.15); color: #fb923c; border: 1px dashed rgba(251, 146, 60, 0.5); }

    /* Strategic tier badges */
    .tier-quick-win { background: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid #10b981; }
    .tier-high-impact { background: rgba(59, 130, 246, 0.2); color: #3b82f6; border: 1px solid #3b82f6; }
    .tier-defensive { background: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid #ef4444; }
    .tier-experimental { background: rgba(168, 85, 247, 0.2); color: #a855f7; border: 1px solid #a855f7; }

    /* Custom scrollbars */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #08090d;
    }
    ::-webkit-scrollbar-thumb {
        background: #1e293b;
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #334155;
    }

    /* Streamlit widget tweaks */
    div[data-testid="stMetricValue"] {
        font-weight: 800 !important;
        color: #ffffff !important;
    }
    div[data-testid="stSidebar"] {
        background-color: #0d1017 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
