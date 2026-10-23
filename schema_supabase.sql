-- =========================================================================
-- GrowthRadar Enterprise Telemetry Schema for Supabase (PostgreSQL)
-- Application: VR Player 360° Video Player (com.vrplayer.vrvideoplayer.videos360.vrvideos.vrapp)
-- =========================================================================

-- 1. App Store Reviews & Telemetry Table
CREATE TABLE IF NOT EXISTS app_store_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    package_name TEXT NOT NULL,
    review_id TEXT UNIQUE NOT NULL,
    user_name TEXT,
    score INT CHECK (score BETWEEN 1 AND 5),
    thumbs_up INT DEFAULT 0,
    content TEXT NOT NULL,
    category TEXT NOT NULL,
    sentiment TEXT NOT NULL,
    sentiment_score NUMERIC(3, 2),
    app_version TEXT,
    review_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexing for high-speed temporal & category queries
CREATE INDEX IF NOT EXISTS idx_reviews_pkg_date ON app_store_reviews(package_name, review_date DESC);
CREATE INDEX IF NOT EXISTS idx_reviews_category ON app_store_reviews(category);
CREATE INDEX IF NOT EXISTS idx_reviews_score ON app_store_reviews(score);


-- 2. AdMob Performance Telemetry Table
CREATE TABLE IF NOT EXISTS admob_daily_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    package_name TEXT NOT NULL,
    metric_date DATE NOT NULL,
    ad_unit_id TEXT,
    ad_format TEXT, -- 'INTERSTITIAL', 'REWARDED', 'BANNER', 'NATIVE'
    impressions INT NOT NULL DEFAULT 0,
    clicks INT DEFAULT 0,
    estimated_revenue NUMERIC(10, 4) NOT NULL DEFAULT 0.0,
    ecpm NUMERIC(8, 2) NOT NULL DEFAULT 0.0,
    match_rate NUMERIC(5, 2) DEFAULT 0.0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(package_name, metric_date, ad_format)
);

CREATE INDEX IF NOT EXISTS idx_admob_date ON admob_daily_metrics(metric_date DESC);


-- 3. Google Ads User Acquisition (UA) Telemetry Table
CREATE TABLE IF NOT EXISTS google_ads_campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    package_name TEXT NOT NULL,
    campaign_id TEXT NOT NULL,
    campaign_name TEXT NOT NULL,
    metric_date DATE NOT NULL,
    cost NUMERIC(10, 2) NOT NULL DEFAULT 0.0,
    conversions_installs INT NOT NULL DEFAULT 0,
    cpi NUMERIC(6, 3) NOT NULL DEFAULT 0.0,
    roas NUMERIC(6, 2) DEFAULT 0.0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(campaign_id, metric_date)
);


-- 4. Google Cloud / Android Vitals & Crashlytics Table
CREATE TABLE IF NOT EXISTS android_vitals_telemetry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    package_name TEXT NOT NULL,
    metric_date DATE NOT NULL,
    app_version TEXT NOT NULL,
    crash_free_users_pct NUMERIC(5, 2) NOT NULL,
    anr_rate_pct NUMERIC(5, 2) NOT NULL,
    cold_start_latency_ms INT DEFAULT 0,
    opengles_crash_count INT DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(package_name, metric_date, app_version)
);


-- 5. Monthly Executive Aggregate View
CREATE OR REPLACE VIEW v_monthly_growth_telemetry AS
SELECT 
    TO_CHAR(r.review_date, 'YYYY-MM') AS month_key,
    COUNT(r.id) AS total_reviews,
    ROUND(AVG(r.score), 2) AS avg_store_rating,
    ROUND(AVG(r.sentiment_score), 2) AS avg_sentiment_score,
    COUNT(CASE WHEN r.category = '360° Codec & Crash' THEN 1 END) AS codec_crashes,
    COUNT(CASE WHEN r.category = 'Gyro & Tracking Drift' THEN 1 END) AS gyro_drifts,
    COUNT(CASE WHEN r.category = 'Ad Intrusion & Immersion' THEN 1 END) AS ad_shock_reports
FROM app_store_reviews r
GROUP BY TO_CHAR(r.review_date, 'YYYY-MM')
ORDER BY month_key DESC;
