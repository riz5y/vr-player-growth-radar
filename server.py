import os
from typing import Optional
from datetime import datetime, timedelta
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import pandas as pd

from data_manager import (
    fetch_live_reviews,
    generate_demo_reviews,
    generate_ai_recommendations,
    get_app_metadata,
    get_monthly_growth_telemetry,
    TARGET_PACKAGE,
    CATEGORY_KEYWORDS
)

app = FastAPI(title="GrowthRadar Telemetry API", version="3.5.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(CURRENT_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)

# Master in-memory state
MASTER_DF = generate_demo_reviews(TARGET_PACKAGE, count=300)

APP_STATE = {
    "package": TARGET_PACKAGE,
    "app_info": get_app_metadata(TARGET_PACKAGE),
    "reviews_df": MASTER_DF
}


@app.get("/api/state")
def get_state(
    package: Optional[str] = None,
    preset: Optional[str] = "all", # 7d, 30d, 90d, 6m, 1y, all
    month: Optional[str] = "all",  # e.g. 2026-10, 2026-09
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    global APP_STATE

    target_pkg = package or APP_STATE["package"] or TARGET_PACKAGE
    if package and package != APP_STATE["package"]:
        APP_STATE["package"] = target_pkg
        APP_STATE["app_info"] = get_app_metadata(target_pkg)
        df, _ = fetch_live_reviews(target_pkg, count=300)
        APP_STATE["reviews_df"] = df

    df = APP_STATE["reviews_df"].copy()

    # Apply Temporal Filters
    now = datetime.now()
    if preset == "7d":
        cutoff = now - timedelta(days=7)
        df = df[df['date'] >= cutoff]
    elif preset == "30d":
        cutoff = now - timedelta(days=30)
        df = df[df['date'] >= cutoff]
    elif preset == "90d":
        cutoff = now - timedelta(days=90)
        df = df[df['date'] >= cutoff]
    elif preset == "6m":
        cutoff = now - timedelta(days=180)
        df = df[df['date'] >= cutoff]
    elif preset == "1y":
        cutoff = now - timedelta(days=365)
        df = df[df['date'] >= cutoff]

    if month and month != "all" and 'month_key' in df.columns:
        df = df[df['month_key'] == month]

    if start_date and end_date:
        try:
            s_dt = datetime.strptime(start_date, '%Y-%m-%d')
            e_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            df = df[(df['date'] >= s_dt) & (df['date'] <= e_dt)]
        except Exception:
            pass

    # Mission-Critical KPIs for filtered window
    total_revs = len(df)
    avg_score = round(float(df['score'].mean()), 2) if total_revs > 0 else 0.0
    pos_count = int((df['sentiment'] == 'Positive').sum())
    neg_count = int((df['sentiment'] == 'Negative').sum())
    neu_count = int((df['sentiment'] == 'Neutral').sum())
    net_sentiment = round(((pos_count - neg_count) / total_revs) * 100, 1) if total_revs > 0 else 0.0
    
    # VR Defect Metrics
    codec_crashes = int((df['category'] == '360° Codec & Crash').sum())
    gyro_drifts = int((df['category'] == 'Gyro & Tracking Drift').sum())
    thermal_events = int((df['category'] == 'Thermal & Hardware Decoding').sum())
    ad_intrusions = int((df['category'] == 'Ad Intrusion & Immersion').sum())
    optics_issues = int((df['category'] == 'VR Optics & FOV Distortion').sum())
    
    critical_defects = codec_crashes + gyro_drifts + ad_intrusions
    defect_pct = round((critical_defects / total_revs) * 100, 1) if total_revs > 0 else 0.0

    # Category and Star distributions
    cat_dist = df['category'].value_counts().to_dict()
    star_dist = {str(i): int((df['score'] == i).sum()) for i in range(1, 6)}

    # Weekly sentiment trajectory
    df_temp = df.copy()
    if 'date' in df_temp.columns and not df_temp.empty:
        df_temp['week'] = pd.to_datetime(df_temp['date']).dt.to_period('W').dt.start_time
        weekly_trend = (
            df_temp.groupby('week')['sentiment_score']
            .mean()
            .reset_index()
            .sort_values('week')
        )
        trajectory = [
            {"date": row['week'].strftime('%b %d'), "sentiment": round(float(row['sentiment_score']), 2)}
            for _, row in weekly_trend.iterrows()
        ]
    else:
        trajectory = []

    # App version churn
    if 'version' in df_temp.columns and not df_temp.empty:
        neg_vers = (
            df_temp[df_temp['score'] <= 2]['version']
            .value_counts()
            .head(6)
            .to_dict()
        )
    else:
        neg_vers = {}

    # Monthly Cohorts Data (AdMob + Google Ads + Android Vitals)
    monthly_telemetry = get_monthly_growth_telemetry()

    # Tactical Directives
    experiments = generate_ai_recommendations(df)

    # Records for Explorer
    records = df[[
        'review_id', 'user_name', 'content', 'score', 'thumbs_up', 'category', 'sentiment', 'sentiment_score', 'version'
    ]].to_dict(orient='records')

    if 'date' in df.columns:
        dates = df['date'].dt.strftime('%Y-%m-%d').tolist()
        for idx, r in enumerate(records):
            r['date'] = dates[idx]

    return {
        "status": "success",
        "system_time": "SYS.ONLINE // 2026.10.23",
        "package": APP_STATE["package"],
        "app_info": APP_STATE["app_info"],
        "filter_applied": {
            "preset": preset,
            "month": month,
            "start_date": start_date,
            "end_date": end_date
        },
        "kpi": {
            "total_reviews": total_revs,
            "avg_score": avg_score,
            "net_sentiment": net_sentiment,
            "pos_count": pos_count,
            "neg_count": neg_count,
            "neu_count": neu_count,
            "critical_defects": critical_defects,
            "defect_pct": defect_pct,
            "codec_crashes": codec_crashes,
            "gyro_drifts": gyro_drifts,
            "thermal_events": thermal_events,
            "ad_intrusions": ad_intrusions,
            "optics_issues": optics_issues
        },
        "charts": {
            "categories": cat_dist,
            "stars": star_dist,
            "trajectory": trajectory,
            "version_churn": neg_vers
        },
        "monthly_growth": monthly_telemetry,
        "experiments": experiments,
        "reviews": records
    }


@app.get("/")
def serve_index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "GrowthRadar Telemetry Server Running"}

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
