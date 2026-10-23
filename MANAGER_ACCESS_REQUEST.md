# 🛰️ Data & API Access Request Dossier: Mobile App Growth Intelligence

Use this document to request read-only access from your engineering manager and growth leads. It explains the exact business justification, zero-risk security posture, direct links, and required IAM permissions.

---

## 1. Executive Summary for Management

> *"We are building an internal Growth Intelligence Radar for **VR Player 360° Video Player** (`com.vrplayer.vrvideoplayer.videos360.vrvideos.vrapp`). It correlates customer reviews with AdMob revenue metrics, Google Ads acquisition costs, and Android Vitals to prioritize high-impact product sprints.*
>
> *To automate this dashboard without manual CSV exports, we require **Read-Only** service credentials. No code modifications or write/billing access are required."*

---

## 2. Exact Permissions & Direct Links Needed

### A. Google AdMob (Monetization & Ad Intrusion Telemetry)
* **Purpose:** Correlate user churn with interstitial ad frequency, eCPM fluctuations, and impression density.
* **Direct Console Link:** [Google AdMob Settings](https://apps.admob.com/#settings/account)
* **Access Needed:**
  - **Option 1 (Fastest / Zero Risk):** A monthly CSV report export from AdMob: *Reports > Custom Report > Dimensions: Date, Ad Format | Metrics: Impressions, Estimated Earnings, eCPM*.
  - **Option 2 (API Automated):** Enable **Google Mobile Ads Reporting API** in Google Cloud Console and grant Service Account role:
    - Role: `AdMob API Viewer` (`roles/admob.reportViewer`)

---

### B. Google Cloud & Play Developer Console (Android Vitals & Crash Telemetry)
* **Purpose:** Monitor Crash-Free Users %, ANR (Application Not Responding) rates, and OpenGLES GPU surface exceptions.
* **Direct Console Link:** [Google Play Console - Users & Permissions](https://play.google.com/console/developers/users-and-permissions)
* **Access Needed:**
  - **Invite User / Service Account:**
  - **Permissions Required (Read-Only):**
    - `View app information and download bulk data (read only)`
    - `View financial data, orders, and cancellation survey responses`
    - `Reply to reviews` (optional: read-only review export)

---

### C. Google Ads (User Acquisition & ROAS Analytics)
* **Purpose:** Calculate Blended Customer Acquisition Cost (CAC), Cost-Per-Install (CPI), and Return on Ad Spend (ROAS).
* **Direct Console Link:** [Google Ads Access & Security](https://ads.google.com/aw/access/users)
* **Access Needed:**
  - **User Role:** `Read Only` access to the Ads Account containing the VR Player universal app campaigns (UAC).

---

### D. Supabase (Free Production Cloud Database)
* **Purpose:** 24/7 cloud persistence for daily review historical sync and AdMob telemetry.
* **Direct Link:** [Supabase New Project](https://supabase.com/dashboard)
* **Credentials Needed:**
  - `SUPABASE_URL`
  - `SUPABASE_ANON_KEY` or `DATABASE_URL` (PostgreSQL connection string)
  - Run the pre-written `schema_supabase.sql` script in Supabase SQL Editor.

---

## 3. Ready-to-Send Email / Slack Message to Your Manager

**Subject:** Request: Read-Only Analytics & Store Access for VR Player Growth Intelligence Tool

Hi [Manager Name],

I’ve been developing an internal performance & growth dashboard for **VR Player 360°** (`com.vrplayer.vrvideoplayer.videos360.vrvideos.vrapp`). 

It analyzes user review trends, categorizes recurring friction (such as gyro drift and in-headset ad interruptions), and maps them into prioritized engineering directives. 

To help us connect review sentiment directly with actual business impact (AdMob revenue, Google Ads CPI, and Android Vitals crash rates), I would like to request read-only access to our analytics sources:

1. **Google Play Console:** Read-only access to download store reviews and Android Vitals.
2. **Google AdMob:** Read-only access or a sample CSV export of our monthly impressions/eCPM.
3. **Google Ads:** Read-only access to view install campaigns and blended CPI.

This is strictly **read-only**—no billing permissions, production code access, or write capabilities are needed. 

I’d be happy to show you a 5-minute live demo of the telemetry dashboard running on localhost today so you can see how it works and the insights it produces.

Thanks,  
[Your Name]
