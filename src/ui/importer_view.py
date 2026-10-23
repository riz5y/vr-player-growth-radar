"""
src/ui/importer_view.py
Section 6: Data Import & Management.
Drag-and-drop CSV validation, schema guidance, quarantine reporting, and synthetic dataset toggling.
"""

import io
import streamlit as st
import pandas as pd
from pathlib import Path
from src.database import DatabaseManager
from src.importer import ReviewImporter
from src.scoring import derive_opportunities_from_reviews


def render_importer_view(db: DatabaseManager, selected_app_id: str):
    st.markdown("## 📥 Data Import & Management")
    st.markdown(
        "<p style='color: #94a3b8; font-size: 0.95rem; margin-top: -10px;'>"
        "Ingest custom CSV datasets, validate schema compliance, review quarantined records, or load synthetic benchmarks."
        "</p>",
        unsafe_allow_html=True
    )

    tab_upload, tab_synthetic, tab_schema, tab_db = st.tabs([
        "📤 CSV File Ingest", "🧪 Synthetic Data Controls", "📖 Schema Reference", "💾 Database Health"
    ])

    with tab_upload:
        st.markdown("### Upload Review CSV")
        uploaded_file = st.file_uploader(
            "Choose a CSV file containing mobile app reviews",
            type=["csv"],
            help="Supports standard schema headers (review_text, rating, review_date, etc.) and common column aliases."
        )

        app_name_override = st.text_input("Default App Name (if missing in CSV)", value="VR Video Player 360")
        app_id_override = st.text_input("Default Package Name (if missing in CSV)", value="com.vrplayer.vrvideoplayer.videos360.vrvideos.vrapp")
        mark_as_synthetic = st.checkbox("Flag uploaded reviews as Synthetic/Demo data", value=False)

        if uploaded_file is not None:
            if st.button("🚀 Process & Ingest CSV", type="primary"):
                try:
                    bytes_io = io.BytesIO(uploaded_file.getvalue())
                    result = ReviewImporter.import_from_csv(
                        bytes_io,
                        default_app_name=app_name_override,
                        default_app_id=app_id_override,
                        force_synthetic_flag=mark_as_synthetic,
                    )

                    st.markdown("#### Ingestion Validation Results")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Valid Rows Ingested", f"{result.valid_count:,}")
                    col2.metric("Duplicates Ignored", f"{result.duplicate_count:,}")
                    col3.metric("Quarantined Invalid Rows", f"{result.quarantine_count:,}")

                    if result.valid_count > 0:
                        db_res = db.save_reviews(result.valid_records)
                        # Re-derive opportunities
                        df = db.get_reviews_df(app_identifier=app_id_override)
                        opps = derive_opportunities_from_reviews(df)
                        db.save_opportunities(opps)
                        st.success(f"Successfully saved {db_res['inserted']} new reviews and updated {db_res['updated']} existing reviews to SQLite!")

                    if result.quarantined_rows:
                        st.warning(f"{result.quarantine_count} rows failed validation and were quarantined.")
                        with st.expander("⚠️ View Quarantined Rows & Validation Error Reasons"):
                            q_df = pd.DataFrame([
                                {
                                    "Row": q["row_index"],
                                    "Validation Errors": "; ".join(q["reasons"]),
                                    "Raw Snippet": str(q["raw_data"])[:120] + "..."
                                }
                                for q in result.quarantined_rows
                            ])
                            st.dataframe(q_df, use_container_width=True, hide_index=True)

                except Exception as e:
                    st.error(f"Failed to process CSV file: {str(e)}")

    with tab_synthetic:
        st.markdown("### 🧪 Synthetic Data Generation & Controls")
        st.markdown(
            "This prototype runs locally and does not require private company credentials. "
            "You can load or reset clearly labeled synthetic datasets for testing and executive demos."
        )

        s_col1, s_col2 = st.columns(2)

        with s_col1:
            st.markdown("#### Load Benchmark Data")
            if st.button("⚡ Load 125 Synthetic Android Reviews", use_container_width=True):
                sample_path = Path(__file__).resolve().parent.parent.parent / "data" / "sample_reviews.csv"
                if sample_path.exists():
                    res = ReviewImporter.import_from_csv(str(sample_path), force_synthetic_flag=True)
                    db.save_reviews(res.valid_records)
                    df = db.get_reviews_df(app_identifier=selected_app_id)
                    opps = derive_opportunities_from_reviews(df)
                    db.save_opportunities(opps)
                    st.success(f"Loaded {res.valid_count} synthetic reviews and updated opportunity rankings!")
                    st.rerun()
                else:
                    st.error("Sample dataset file not found at data/sample_reviews.csv")

        with s_col2:
            st.markdown("#### Clean Database")
            if st.button("🗑️ Wipe All Synthetic Records", use_container_width=True):
                deleted = db.clear_reviews(synthetic_only=True)
                st.info(f"Removed {deleted} synthetic records from SQLite.")
                st.rerun()

    with tab_schema:
        st.markdown("### 📖 Standard Review CSV Schema Specification")
        st.markdown("""
        Every imported CSV should ideally provide the following columns (column aliases are automatically resolved):

        | Column | Type | Required | Description | Aliases Supported |
        | :--- | :--- | :--- | :--- | :--- |
        | `app_name` | String | Yes | Human-readable app title | `appname`, `title`, `application` |
        | `app_identifier` | String | Yes | Android package name or iOS bundle ID | `package_name`, `app_id`, `bundle_id` |
        | `review_id` | String | Yes | Unique store identifier (auto-hashed if blank) | `id`, `reviewid`, `uuid` |
        | `review_date` | Date/ISO | Yes | Date review was published | `date`, `created_at`, `timestamp` |
        | `rating` | Integer | Yes | Numeric star rating (1 to 5) | `score`, `stars`, `star_rating` |
        | `review_text` | String | Yes | Full text body of the user feedback | `text`, `content`, `body`, `comment` |
        | `review_language`| String | No | ISO language code (defaults to 'en') | `language`, `lang` |
        | `source` | String | No | Platform origin (defaults to 'google_play') | `platform`, `store` |
        | `developer_reply`| String | No | Developer response text if present | `reply`, `dev_reply` |
        | `is_synthetic` | Boolean| No | Tag indicating test/demo data (default False) | `synthetic`, `demo_data` |
        """)

        sample_csv_template = (
            "app_name,app_identifier,review_id,review_date,rating,review_text,review_language,source\n"
            "VR Video Player 360,com.vrplayer.vrvideoplayer.videos360.vrvideos.vrapp,rev_001,2026-10-22,1,\"App crashed on 4K MKV file.\",en,google_play\n"
            "VR Video Player 360,com.vrplayer.vrvideoplayer.videos360.vrvideos.vrapp,rev_002,2026-10-22,5,\"Super smooth playback in cardboard mode!\",en,google_play\n"
        )
        st.download_button(
            "📥 Download Standard CSV Template",
            data=sample_csv_template,
            file_name="app_review_standard_template.csv",
            mime="text/csv",
        )

    with tab_db:
        st.markdown("### 💾 Local SQLite Diagnostics")
        stats = db.get_database_stats()
        st.json(stats)
        st.caption(f"Database location on disk: `{stats['db_path']}`")
