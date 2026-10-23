"""
src/ui/reviews_view.py
Section 2: Review Intelligence.
Drill-down filters, 9-bucket categorization, manual classification overrides, and CSV export.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from src.database import DatabaseManager
from src.models import ALL_CATEGORIES
from src.importer import ReviewImporter


def render_reviews_view(db: DatabaseManager, selected_app_id: str):
    st.markdown("## 🔍 Review Intelligence")
    st.markdown(
        "<p style='color: #94a3b8; font-size: 0.95rem; margin-top: -10px;'>"
        "Granular review analysis, 9-bucket classification, manual category corrections, and data export."
        "</p>",
        unsafe_allow_html=True
    )

    df_all = db.get_reviews_df(app_identifier=selected_app_id)
    if df_all.empty:
        st.warning("No reviews found for this application. Please import data first.")
        return

    # 1. Filter Control Bar
    with st.expander("🎛️ Filter Controls", expanded=True):
        f_col1, f_col2, f_col3, f_col4 = st.columns([3, 3, 3, 3])

        with f_col1:
            category_options = ["All Categories"] + ALL_CATEGORIES
            selected_cat = st.selectbox("Category Bucket", category_options, index=0)

        with f_col2:
            min_r, max_r = st.slider("Star Rating Range", 1, 5, (1, 5))

        with f_col3:
            min_date = df_all["review_date"].min().date()
            max_date = df_all["review_date"].max().date()
            date_range = st.date_input("Date Range", value=(min_date, max_date))

        with f_col4:
            search_query = st.text_input("Search Keyword", placeholder="e.g. freeze, ads, gyro")

    # Apply date filters
    start_d = date_range[0] if isinstance(date_range, (list, tuple)) and len(date_range) > 0 else min_date
    end_d = date_range[1] if isinstance(date_range, (list, tuple)) and len(date_range) > 1 else max_date

    # Query filtered DataFrame
    filtered_df = db.get_reviews_df(
        app_identifier=selected_app_id,
        category=selected_cat if selected_cat != "All Categories" else None,
        min_rating=min_r,
        max_rating=max_r,
        start_date=start_d.isoformat(),
        end_date=end_d.isoformat(),
        search_query=search_query,
    )

    # 2. Summary stats for filtered slice
    f_total = len(filtered_df)
    f_avg = filtered_df["rating"].mean() if f_total > 0 else 0.0

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Matching Reviews", f"{f_total:,}")
    with m2:
        st.metric("Slice Avg Rating", f"{f_avg:.2f} ★")
    with m3:
        st.metric("Total Store Volume", f"{len(df_all):,}")
    with m4:
        # Export CSV Button
        if not filtered_df.empty:
            csv_export_data = ReviewImporter.export_to_csv(filtered_df)
            st.download_button(
                label="📥 Export Slice to CSV",
                data=csv_export_data,
                file_name=f"reviews_export_{selected_cat.replace(' ', '_')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

    st.markdown("---")

    if filtered_df.empty:
        st.info("No reviews matched your filter parameters. Try broadening your criteria.")
        return

    # 3. Rating Distribution & Category Breakdown for slice
    g_col1, g_col2 = st.columns([6, 6])
    with g_col1:
        st.markdown("##### Rating Distribution in Filtered Slice")
        rating_counts = filtered_df["rating"].value_counts().reindex([1, 2, 3, 4, 5], fill_value=0).reset_index()
        rating_counts.columns = ["rating", "count"]
        rating_counts["rating_label"] = rating_counts["rating"].astype(str) + " Stars"

        fig_ratings = px.bar(
            rating_counts,
            x="rating_label",
            y="count",
            color="rating",
            color_continuous_scale=["#ef4444", "#f59e0b", "#3b82f6", "#10b981"],
            labels={"count": "Reviews", "rating_label": "Stars"}
        )
        fig_ratings.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0),
            height=240,
            showlegend=False,
            coloraxis_showscale=False,
            xaxis=dict(color="#94a3b8"),
            yaxis=dict(color="#94a3b8", gridcolor="rgba(255,255,255,0.05)"),
        )
        st.plotly_chart(fig_ratings, use_container_width=True)

    with g_col2:
        st.markdown("##### Category Share")
        cat_share = filtered_df["effective_category"].value_counts().reset_index()
        cat_share.columns = ["category", "count"]
        fig_cat = px.bar(
            cat_share,
            x="count",
            y="category",
            orientation="h",
            color="count",
            color_continuous_scale="Blues",
        )
        fig_cat.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0),
            height=240,
            coloraxis_showscale=False,
            xaxis=dict(color="#94a3b8", gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(color="#94a3b8"),
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    # 4. Review Inspection and Manual Classification Override
    st.markdown("### 📋 Verbatim Review Log & Manual Classification Correction")
    st.markdown(
        "<p style='color: #94a3b8; font-size: 0.88rem; margin-top: -6px;'>"
        "Inspect supporting reviews. If any review is misclassified, use the manual correction tool below."
        "</p>",
        unsafe_allow_html=True
    )

    # Manual Override Box
    with st.expander("✏️ Correct a Review's Category", expanded=False):
        c_left, c_mid, c_right = st.columns([4, 4, 2])
        with c_left:
            review_options = {
                f"[{r['rating']}★] {r['review_id']} - {r['review_text'][:60]}...": r['review_id']
                for _, r in filtered_df.head(40).iterrows()
            }
            selected_review_label = st.selectbox("Select Review to Correct", list(review_options.keys()))
            target_review_id = review_options[selected_review_label] if review_options else None
        
        with c_mid:
            new_target_cat = st.selectbox("Assign Correct Category", ALL_CATEGORIES, index=0)

        with c_right:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Save Correction", type="primary", use_container_width=True):
                if target_review_id:
                    db.update_review_category(target_review_id, new_target_cat)
                    st.success(f"Updated {target_review_id} to '{new_target_cat}'! Reloading...")
                    st.rerun()

    # Table Display
    display_df = filtered_df[[
        "review_id", "review_date", "rating", "effective_category", "sentiment_score", "review_text"
    ]].copy()
    display_df["review_date"] = display_df["review_date"].dt.strftime("%Y-%m-%d")
    display_df.columns = ["ID", "Date", "Rating", "Assigned Category", "Sentiment", "Review Text"]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Rating": st.column_config.NumberColumn(format="%d ★"),
            "Sentiment": st.column_config.ProgressColumn(min_value=-1.0, max_value=1.0, format="%.2f"),
            "Review Text": st.column_config.TextColumn(width="large"),
        }
    )
