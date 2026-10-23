# ⚡ Mobile App Growth Intelligence System (App Opportunity Radar)

An internal product growth intelligence system that analyzes consumer app-store reviews, categorizes user complaints, and translates evidence into ranked, sprint-ready product and marketing experiments.

---

## 🌟 Key Features

1. **Opportunity Radar**: 
   - Automatic classification into 6 core themes: *Critical Bug/Crash*, *Performance & Battery*, *Ads & Paywall*, *UI/UX Confusion*, *Feature Requests*, and *Billing/Support*.
   - Net Sentiment calculation and star rating breakdown.
2. **AI Growth Experiment Backlog**:
   - Impact vs. Effort quadrant matrix (Quick Wins vs Strategic Bets).
   - Generates testable hypotheses with real user quotes, target business metrics, and Jira-ready export cards.
3. **Dual Ingestion Mode**:
   - **Sample Demo Mode**: Realistic 200+ consumer app dataset for instant demonstrations.
   - **Live Google Play Ingestion**: Real-time public review fetcher for any Play Store package ID.
4. **Cloud-Ready**:
   - 100% ready to deploy to Streamlit Community Cloud (free) or containerized on Render/GCP.
   - Includes GitHub Actions workflow for automated daily review scraping.

---

## 🚀 Running Locally

From this directory:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch the Streamlit dashboard
python -m streamlit run app.py
```

The dashboard will open automatically at `http://localhost:8501`.

---

## ☁️ Deploying Live on the Web (Free & 24/7)

### Streamlit Community Cloud (Recommended)
1. Initialize git and push this folder to your GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of Growth Intelligence System"
   git branch -M main
   git remote add origin https://github.com/<YOUR_USER>/mobile-app-growth-intelligence.git
   git push -u origin main
   ```
2. Visit [share.streamlit.io](https://share.streamlit.io) and log in with GitHub.
3. Click **"New App"**, pick your repository and set `Main file path` to `app.py`.
4. Click **Deploy!** In ~2 minutes you have a permanent public/private URL (e.g. `https://growth-radar.streamlit.app`).

---

## 📅 30-Day Execution Roadmap

- [x] **Phase 1 (Days 1–3)**: Foundation & Interface architecture.
- [ ] **Phase 2 (Days 4–10)**: Connect first company app or competitor package ID; test scraper reliability.
- [ ] **Phase 3 (Days 11–17)**: Add LLM API integration (OpenAI/Gemini/Anthropic) for dynamic multi-sentence summarization.
- [ ] **Phase 4 (Days 18–24)**: Validate accuracy against manual review samples.
- [ ] **Phase 5 (Days 25–30)**: Pitch to manager with live web demo and request internal data access.
