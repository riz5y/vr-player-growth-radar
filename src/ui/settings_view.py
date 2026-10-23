"""
src/ui/settings_view.py
Section 7: Settings & Data Sources.
Configures default weights presets, optional AI provider keys, and executive presentation guides.
"""

import streamlit as st
from src.database import DatabaseManager, DEFAULT_WEIGHTS

WEIGHT_PRESETS = {
    "Balanced Growth (Default)": {
        "weight_frequency": 1.5,
        "weight_severity": 2.5,
        "weight_affected_users": 1.5,
        "weight_strategic_relevance": 2.0,
        "weight_evidence_strength": 1.5,
        "weight_effort": 1.5,
    },
    "Aggressive Rating Defense (Churn Stop)": {
        "weight_frequency": 2.0,
        "weight_severity": 4.5,
        "weight_affected_users": 2.5,
        "weight_strategic_relevance": 1.5,
        "weight_evidence_strength": 2.0,
        "weight_effort": 1.0,
    },
    "Low-Hanging Fruit (Fast Engineering Wins)": {
        "weight_frequency": 2.5,
        "weight_severity": 2.0,
        "weight_affected_users": 1.5,
        "weight_strategic_relevance": 1.5,
        "weight_evidence_strength": 1.5,
        "weight_effort": 3.5,
    },
}


def render_settings_view(db: DatabaseManager):
    st.markdown("## ⚙️ Settings & Configuration")
    st.markdown(
        "<p style='color: #94a3b8; font-size: 0.95rem; margin-top: -10px;'>"
        "Manage prioritization presets, optional LLM providers, and manager briefing templates."
        "</p>",
        unsafe_allow_html=True
    )

    t1, t2, t3 = st.tabs(["Prioritization Presets", "AI Provider Setup", "Manager Presentation Guide"])

    with t1:
        st.markdown("### ⚖️ Prioritization Presets")
        st.markdown("Select a strategic preset to apply instant mathematical weight configurations:")

        chosen_preset = st.selectbox("Strategic Preset", list(WEIGHT_PRESETS.keys()))
        if st.button("Apply Preset Weights", type="primary"):
            db.save_setting("prioritization_weights", WEIGHT_PRESETS[chosen_preset])
            st.success(f"Applied preset '{chosen_preset}'! Switch to Opportunity Prioritization to inspect new rankings.")

        current = db.get_setting("prioritization_weights", DEFAULT_WEIGHTS)
        st.json(current)

    with t2:
        st.markdown("### 🤖 Intelligence Provider Abstraction")
        st.markdown(
            "By default, App Opportunity Radar runs **100% offline at zero cost** using a deterministic "
            "semantic heuristic engine. If you wish to connect an optional LLM for synthesis, configure it below:"
        )

        provider_mode = st.radio(
            "AI Engine Mode",
            ["Deterministic Heuristic (Offline / Zero Cost / No API Key)", "Google Gemini API", "OpenAI API"],
            index=0
        )

        if "Gemini" in provider_mode or "OpenAI" in provider_mode:
            api_key = st.text_input("Enter API Key", type="password", placeholder="AIza... or sk-...")
            if st.button("Save API Key Locally"):
                st.session_state["AI_API_KEY"] = api_key
                st.success("API key saved for this active session (not stored in public git repo).")
        else:
            st.info("Operating in Deterministic Heuristic mode. High performance, zero latency, zero API costs.")

    with t3:
        st.markdown("### 💼 How to Present Findings to Management")
        st.markdown("""
        When sharing findings with engineering leads and product managers, use an evidence-first, 3-part structure:

        #### 1. The Executive Slack Update Template
        ```text
        *App Opportunity Radar — Weekly Synthesis Brief*
        App: VR Video Player 360 (com.vrplayer...)
        Dataset: 125 store reviews analyzed | Current Rating: 2.82★

        🚨 Top User Problem:
        4K MKV & HEVC files fail with black screen / freeze (18% of reviews, avg rating 1.2★).
        Caused by hardware decoder crashes on mid-tier chipsets.

        💡 Recommended Fast Fix:
        Add ExoPlayer software decoder fallback (Media3 ffmpeg extension).
        Priority Score: 14.5 / 100 Index: 92 (Rank #1).

        🎯 Next Engineering Step:
        Inspect Kotlin ExoPlayer initialization in app/src/main/java and add CodecSelector fallback hook.
        ```

        #### 2. Why Internal Read-Only Access is Warranted
        - **Demonstrated Prototype**: You have already proven that review analytics uncover specific revenue-impacting issues.
        - **Zero Risk**: Read-only access to Google Play Console reviews or AdMob reporting entails zero write risk to production code.
        """)
