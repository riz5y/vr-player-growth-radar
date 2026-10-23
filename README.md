# App Opportunity Radar ⚡
**Internal Product & Growth Intelligence Platform for Mobile Applications**

---

## 1. Business Objective & Problem Solved
App Opportunity Radar is an evidence-first internal intelligence platform designed for mobile app publishers and Android engineering teams. It bridges the gap between raw store reviews, user churn signals, and engineering roadmaps by answering six critical questions:

1. **What are users complaining about most?** (Categorized across 9 standardized feedback buckets).
2. **Which features are users requesting most urgently?**
3. **What critical bugs or monetization blockers are damaging store ratings and 7-day retention?**
4. **How do competing apps position themselves and where are their vulnerabilities?**
5. **Which product improvements should engineering prioritize first based on transparent return-on-investment?**
6. **Which recommendations are supported by hard evidence vs. exploratory hypotheses?**

---

## 2. Architecture & Modular Structure

The codebase is engineered with strict separation of concerns, zero required external cloud accounts, and 100% offline local persistence:

```
mobile-app-growth-intelligence/
├── data/
│   ├── app_radar.db               # Local SQLite database (auto-created on startup)
│   ├── sample_reviews.csv         # 100+ standard Android reviews (explicitly marked is_synthetic=True)
│   └── sample_competitors.csv     # Competitor benchmark data
├── src/
│   ├── models.py                  # Pydantic schemas enforcing standard schema & AI outputs
│   ├── database.py                # SQLite repository managing CRUD, indices, and manual overrides
│   ├── importer.py                # Resilient CSV parser, date normalizer, deduplicator & quarantine logger
│   ├── classifier.py              # Deterministic 9-category taxonomy & sentiment polarity engine
│   ├── scoring.py                 # Multi-factor mathematical opportunity prioritization engine
│   ├── ai_analyzer.py             # Dual-mode intelligence (Zero-cost heuristic + optional LLM)
│   └── ui/
│       ├── styles.py              # Dark glassmorphism & typography injection
│       ├── overview.py            # Section 1: Executive Overview (KPIs, trajectory, briefings)
│       ├── reviews_view.py        # Section 2: Review Intelligence (drilldown, manual correction, export)
│       ├── insights_view.py       # Section 3: AI Insights & Grounded Recommendations
│       ├── competitors_view.py    # Section 4: Competitor Intelligence & Benchmarking
│       ├── prioritization_view.py # Section 5: Opportunity Prioritization Matrix
│       ├── importer_view.py       # Section 6: Data Import & Management
│       └── settings_view.py       # Section 7: Settings & Data Sources
├── tests/
│   ├── test_models.py             # Pydantic schema validation tests
│   ├── test_importer.py           # Ingestion, bad formats, duplicate handling
│   ├── test_classifier.py         # 9-category taxonomy & negation rules verification
│   ├── test_scoring.py            # Prioritization formula verification & boundary tests
│   └── test_database.py           # SQLite persistence & manual classification override tests
├── app.py                         # Streamlit application entry point & router
├── requirements.txt               # Pinned dependencies
└── README.md                      # Platform documentation
```

---

## 3. Technology Stack
- **Python 3.10+ / 3.14**
- **Streamlit**: Modern dark dashboard with glassmorphism UI.
- **SQLite3**: Zero-configuration, zero-cost local persistence.
- **pandas**: High-performance data cleaning, aggregation, and filtering.
- **Plotly**: Interactive charts (rolling 7-day trajectories, category donuts, rating histograms).
- **Pydantic (v2)**: Strict type checking, input validation, and structured recommendation schemas.
- **pytest**: Automated testing suite covering data pipelines and mathematical formulas.

---

## 4. Standard CSV Data Schema

The platform accepts CSV exports from Google Play Console, App Store, AppFollow, or custom scraping scripts. The canonical schema is:

| Column | Type | Required | Description | Supported Aliases |
| :--- | :--- | :--- | :--- | :--- |
| `app_name` | String | Yes | Human-readable app title | `appname`, `title`, `application` |
| `app_identifier` | String | Yes | Package name (e.g. `com.vrplayer...`) | `package_name`, `app_id`, `bundle_id` |
| `review_id` | String | Yes | Unique review ID (auto-generated if empty) | `id`, `reviewid`, `uuid` |
| `review_date` | Date/ISO | Yes | Date review was published | `date`, `created_at`, `timestamp` |
| `rating` | Integer | Yes | Numeric star rating (1 to 5) | `score`, `stars`, `star_rating` |
| `review_text` | String | Yes | Verbatim user feedback | `text`, `content`, `body`, `comment` |
| `review_language`| String | No | ISO language code (default `'en'`) | `language`, `lang` |
| `source` | String | No | Platform origin (default `'google_play'`) | `platform`, `store` |
| `developer_reply`| String | No | Developer response text if present | `reply`, `dev_reply` |
| `is_synthetic` | Boolean| No | Demo data tag (default `False`) | `synthetic`, `demo_data` |

*Malformed records (missing text, unparseable dates, ratings outside 1–5) are safely isolated into a Quarantine list with exact failure reasons.*

---

## 5. Review Classification Taxonomy (9 Mandatory Buckets)

Every review is automatically classified into one of 9 standardized categories:
1. **Bugs and crashes**: Critical playback freezes, black screens, force closes, ANRs.
2. **Performance**: Frame rate drops, heating, stutter, battery drain, latency.
3. **User interface and usability**: Menu navigation, gyro drift, font readability, head tracking.
4. **Advertising and monetization**: Interstitials in VR mode, popup frequency, unskippable ads.
5. **Missing features**: Subtitles (.SRT), MKV/HEVC codecs, network streaming (SMB/DLNA).
6. **Account and onboarding**: Permissions requests, tutorials, login issues.
7. **Pricing and subscriptions**: Subscriptions, paywalls, refund complaints.
8. **Positive feedback**: 4-5★ praise, feature compliments, recommendations.
9. **Other**: General feedback without distinct category signals.

*Users can manually correct any misclassified review directly in Section 2, updating SQLite immediately.*

---

## 6. Opportunity Prioritization Mathematical Model

The ranking score transparently models the return on engineering investment:

$$\text{Priority Score} = \left( \frac{w_F \cdot F + w_S \cdot S + w_A \cdot A + w_R \cdot R + w_{ES} \cdot ES}{w_E \cdot E} \right) \times C$$

Where:
- **$F$ (Frequency)**: How often the issue occurs (1 to 5).
- **$S$ (Severity)**: Impact on rating drag or blocker level (1 to 5).
- **$A$ (Affected Users)**: Estimated user segment impacted (1 to 5).
- **$R$ (Strategic Relevance)**: Business alignment with retention/growth goals (1 to 5).
- **$ES$ (Evidence Strength)**: Volume and consistency of supporting reviews (1 to 5).
- **$E$ (Implementation Effort)**: Engineering/QA effort required (1 to 5).
- **$C$ (Confidence Multiplier)**: Data certainty (0.5 to 1.0).

*Weights ($w_F, w_S, w_A, w_R, w_{ES}, w_E$) can be dynamically adjusted in real-time in Section 5 or loaded via presets in Settings.*

---

## 7. Setup & Run Instructions (Windows)

### Prerequisites
- Python 3.10+ installed and on PATH.

### Installation
Open PowerShell in the project directory:

```powershell
cd C:\Users\RIZWANPC\.gemini\antigravity\scratch\mobile-app-growth-intelligence

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```powershell
streamlit run app.py
```
The application will launch in your default browser at `http://localhost:8501`.

### Running Automated Tests
```powershell
$env:PYTHONPATH="C:\Users\RIZWANPC\.gemini\antigravity\scratch\mobile-app-growth-intelligence"
python -m pytest tests -v
```

---

## 8. How to Present Findings to Management

When presenting to engineering leads or product managers:
1. **Highlight Demonstrated Value**: Walk through the Executive Overview to show the direct correlation between the **4K Codec / Black Screen issue** and 1-star rating drag.
2. **Demonstrate ROI**: Use Section 5 (Opportunity Prioritization) to show why a software decoder fallback in Kotlin is the #1 highest-ROI fix.
3. **Request Read-Only Credentials**: Use `MANAGER_ACCESS_REQUEST.md` to request read-only Google Play Console review export access, demonstrating that no production risk or paid infrastructure is required.
