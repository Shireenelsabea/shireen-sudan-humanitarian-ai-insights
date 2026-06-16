from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DOCS_DIR = ROOT / "docs"


SECTOR_KEYWORDS = {
    "Food Security": [
        "food",
        "meal",
        "meals",
        "flour",
        "sorghum",
        "bread",
        "ration",
        "rations",
        "hungry",
        "milk",
        "cash",
        "prices",
        "oil",
    ],
    "WASH": [
        "water",
        "latrine",
        "latrines",
        "toilet",
        "soap",
        "hygiene",
        "sanitation",
        "hand pump",
        "tank",
        "unsafe water",
        "stomach",
    ],
    "Health": [
        "clinic",
        "medicine",
        "fever",
        "malaria",
        "health",
        "doctor",
        "pregnant",
        "pregnancy",
        "delivery",
        "test kits",
        "sick",
        "blood pressure",
    ],
    "Shelter": [
        "shelter",
        "shelters",
        "tent",
        "plastic sheet",
        "sheets",
        "rain",
        "flood",
        "blanket",
        "blankets",
        "shade",
        "sleeping outside",
        "privacy",
    ],
    "Protection": [
        "unsafe",
        "safety",
        "harassment",
        "women",
        "children",
        "separated",
        "tracing",
        "lights",
        "lighting",
        "checkpoint",
        "violence",
        "safe space",
    ],
    "Registration": [
        "register",
        "registration",
        "documents",
        "list",
        "missed",
        "new arrivals",
    ],
}

CRITICAL_TERMS = [
    "no ",
    "not enough",
    "unsafe",
    "sick",
    "children",
    "separated",
    "blocked",
    "flood",
    "malaria",
    "ran out",
    "sleeping outside",
]

RECOMMENDATIONS = {
    "idp_pressure": "Use caseload size to frame the immediate ask and split support by settlement capacity.",
    "food_insecurity_pct": "Preposition food rations and review cash values against local prices.",
    "wash_gap_pct": "Deploy a mobile WASH team for water points, hygiene kits, and latrine safety.",
    "health_gap_pct": "Schedule a mobile clinic rotation with essential medicines and referral support.",
    "access_constraint": "Escalate access planning and prepare remote support through local partners.",
    "protection_alerts": "Trigger protection case review and strengthen safe reporting channels.",
    "funding_gap_pct": "Prepare donor note with caseload, gap, and immediate operational ask.",
}

DRIVER_LABELS = {
    "idp_pressure": "IDP volume",
    "food_insecurity_pct": "Food security",
    "wash_gap_pct": "WASH",
    "health_gap_pct": "Health",
    "access_constraint": "Access",
    "protection_alerts": "Protection",
    "funding_gap_pct": "Funding",
}

VALIDATION_STEPS = {
    "Critical": [
        "Validate the hotspot with field partners within 24-48 hours.",
        "Check whether protection, WASH, food, and health teams see the same pattern.",
        "Prepare a short donor or coordination note with caseload, driver, and immediate ask.",
    ],
    "High": [
        "Schedule partner validation during the next coordination cycle.",
        "Preposition supplies or service capacity if access conditions are stable.",
        "Monitor feedback volume and sector pressure weekly.",
    ],
    "Elevated": [
        "Keep the area on the watchlist and preserve a baseline for comparison.",
        "Look for sudden increases in feedback, access constraints, or protection alerts.",
        "Use community feedback channels to verify whether the risk is changing.",
    ],
}


def normalize(series: pd.Series) -> pd.Series:
    min_value = series.min()
    max_value = series.max()
    if max_value == min_value:
        return pd.Series(np.ones(len(series)), index=series.index)
    return (series - min_value) / (max_value - min_value)


def score_states(df: pd.DataFrame) -> pd.DataFrame:
    scored = df.copy()
    scored["protection_pressure"] = normalize(scored["protection_alerts"])
    scored["priority_score"] = (
        normalize(scored["idps"]) * 0.26
        + scored["food_insecurity_pct"] * 0.20
        + scored["wash_gap_pct"] * 0.15
        + scored["health_gap_pct"] * 0.12
        + scored["access_constraint"] * 0.12
        + scored["protection_pressure"] * 0.10
        + scored["funding_gap_pct"] * 0.05
    ) * 100
    scored["priority_score"] = scored["priority_score"].round(1)
    scored["children_estimate"] = (scored["idps"] * scored["children_share"]).round().astype(int)
    scored["priority_level"] = pd.cut(
        scored["priority_score"],
        bins=[0, 62, 74, 100],
        labels=["Elevated", "High", "Critical"],
        include_lowest=True,
    ).astype(str)
    return scored


def classify_feedback(text: str) -> dict[str, object]:
    lowered = f" {text.lower()} "
    sector_scores = {
        sector: sum(1 for keyword in keywords if keyword in lowered)
        for sector, keywords in SECTOR_KEYWORDS.items()
    }
    top_sector = max(sector_scores, key=sector_scores.get)
    top_score = sector_scores[top_sector]
    if top_score == 0:
        top_sector = "Unclassified"

    critical_hits = sum(1 for term in CRITICAL_TERMS if term in lowered)
    urgency_points = top_score + critical_hits
    if urgency_points >= 4:
        urgency = "Critical"
    elif urgency_points >= 2:
        urgency = "High"
    else:
        urgency = "Medium"

    if urgency == "Critical":
        sentiment = "Distress signal"
    elif urgency == "High":
        sentiment = "Negative"
    else:
        sentiment = "Needs follow-up"

    confidence = min(0.96, 0.48 + (top_score * 0.12) + (critical_hits * 0.04))
    matched_terms = [
        keyword
        for keyword in SECTOR_KEYWORDS.get(top_sector, [])
        if keyword in lowered
    ][:5]

    return {
        "sector": top_sector,
        "urgency": urgency,
        "sentiment": sentiment,
        "confidence": round(confidence, 2),
        "matched_terms": matched_terms,
    }


def make_forecast(trends: pd.DataFrame, months: int = 3) -> list[dict[str, object]]:
    actual = trends[["month", "total_idps"]].copy()
    actual["series"] = "Observed"

    x = np.arange(len(actual))
    y = actual["total_idps"].to_numpy()
    slope, intercept = np.polyfit(x, y, 1)
    future_x = np.arange(len(actual), len(actual) + months)
    last_month = pd.to_datetime(actual["month"].max())
    future_months = pd.date_range(last_month + pd.offsets.MonthBegin(1), periods=months, freq="MS")

    forecast = pd.DataFrame(
        {
            "month": future_months.strftime("%Y-%m-%d"),
            "total_idps": np.round(slope * future_x + intercept).astype(int),
            "series": "Linear scenario extension",
        }
    )
    actual["month"] = pd.to_datetime(actual["month"]).dt.strftime("%Y-%m-%d")
    return pd.concat([actual, forecast], ignore_index=True).to_dict(orient="records")


def normalize_sector(value: str) -> str:
    return "Protection" if value == "Child Protection" else value


def make_payload() -> dict[str, object]:
    states = score_states(pd.read_csv(DATA_DIR / "state_needs.csv"))
    trends = pd.read_csv(DATA_DIR / "monthly_trends.csv")
    feedback = pd.read_csv(DATA_DIR / "feedback_samples.csv")
    feedback["date"] = pd.to_datetime(feedback["date"]).dt.strftime("%Y-%m-%d")

    classifications = feedback["message"].apply(classify_feedback)
    feedback["ai_sector"] = classifications.apply(lambda item: item["sector"])
    feedback["ai_urgency"] = classifications.apply(lambda item: item["urgency"])
    feedback["confidence"] = classifications.apply(lambda item: item["confidence"])
    feedback["match"] = feedback.apply(
        lambda row: normalize_sector(row["sector"]) == normalize_sector(row["ai_sector"]),
        axis=1,
    )
    trends["month"] = pd.to_datetime(trends["month"]).dt.strftime("%Y-%m-%d")

    return {
        "states": states.to_dict(orient="records"),
        "trends": trends.to_dict(orient="records"),
        "feedback": feedback.to_dict(orient="records"),
        "forecast": make_forecast(trends),
        "sectorKeywords": SECTOR_KEYWORDS,
        "criticalTerms": CRITICAL_TERMS,
        "recommendations": RECOMMENDATIONS,
        "driverLabels": DRIVER_LABELS,
        "validationSteps": VALIDATION_STEPS,
    }


def build_html() -> str:
    payload = json.dumps(make_payload(), separators=(",", ":"))
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Interactive Dashboard | Sudan Humanitarian AI Insights</title>
    <meta name="description" content="Interactive GitHub Pages dashboard for Shireen Al Sabea's Sudan Humanitarian AI Insights project.">
    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    <style>
      :root {{
        --ink: #17202a;
        --muted: #5b6675;
        --line: #d8dee6;
        --paper: #ffffff;
        --canvas: #f5f7f9;
        --green: #1f6f5b;
        --teal: #1f7a8c;
        --amber: #c58a20;
        --red: #b42318;
        --blue: #315a8a;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        font-family: Inter, Arial, Helvetica, sans-serif;
        color: var(--ink);
        background: var(--canvas);
      }}
      a {{ color: inherit; }}
      .topbar {{
        position: sticky;
        top: 0;
        z-index: 10;
        background: rgba(255,255,255,0.95);
        border-bottom: 1px solid var(--line);
        backdrop-filter: blur(12px);
      }}
      .nav {{
        width: min(1380px, calc(100% - 28px));
        margin: 0 auto;
        min-height: 64px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 16px;
      }}
      .brand {{
        display: flex;
        align-items: center;
        gap: 10px;
        font-weight: 850;
        text-decoration: none;
      }}
      .brand img {{
        width: 38px;
        height: 38px;
        object-fit: cover;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: #fff;
      }}
      .nav-links {{
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        color: var(--muted);
        font-weight: 750;
        font-size: 0.92rem;
      }}
      .nav-links a {{ text-decoration: none; }}
      .page {{
        width: min(1380px, calc(100% - 28px));
        margin: 0 auto;
        padding: 24px 0 48px;
      }}
      .hero {{
        display: grid;
        grid-template-columns: minmax(0, 1.35fr) minmax(280px, 0.65fr);
        gap: 18px;
        align-items: stretch;
        margin-bottom: 18px;
      }}
      .panel {{
        border: 1px solid var(--line);
        border-radius: 8px;
        background: var(--paper);
        padding: 18px;
        box-shadow: 0 10px 28px rgba(23,32,42,0.05);
      }}
      .hero-main {{
        display: flex;
        gap: 14px;
        align-items: flex-start;
      }}
      .hero-logo {{
        width: 64px;
        height: 64px;
        border-radius: 12px;
        border: 1px solid var(--line);
        object-fit: cover;
        background: #fff;
        flex: 0 0 auto;
      }}
      .eyebrow {{
        margin: 0 0 8px;
        color: var(--green);
        font-size: 0.8rem;
        font-weight: 900;
        text-transform: uppercase;
      }}
      h1, h2, h3 {{ margin: 0; letter-spacing: 0; }}
      h1 {{
        font-size: clamp(2rem, 4vw, 3.6rem);
        line-height: 1;
        margin-bottom: 12px;
      }}
      h2 {{ font-size: clamp(1.5rem, 3vw, 2.2rem); margin-bottom: 8px; }}
      h3 {{ font-size: 1.05rem; margin-bottom: 8px; }}
      p {{
        color: var(--muted);
        line-height: 1.55;
        margin: 0;
      }}
      .chips {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 14px;
      }}
      .chip {{
        border: 1px solid #cbd5df;
        border-radius: 999px;
        background: #f8fafc;
        color: var(--ink);
        font-size: 0.84rem;
        font-weight: 800;
        padding: 6px 10px;
      }}
      .guardrail-item {{
        display: flex;
        gap: 10px;
        margin-bottom: 10px;
        color: var(--muted);
        line-height: 1.4;
      }}
      .dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--green);
        margin-top: 8px;
        flex: 0 0 auto;
      }}
      .controls {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 14px;
        margin: 18px 0;
      }}
      .control-title {{
        font-weight: 850;
        margin-bottom: 8px;
      }}
      .check-grid {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
      }}
      label.check {{
        display: inline-flex;
        gap: 6px;
        align-items: center;
        border: 1px solid var(--line);
        border-radius: 999px;
        padding: 7px 10px;
        background: #fff;
        cursor: pointer;
        font-weight: 750;
      }}
      label.check input {{ accent-color: var(--green); }}
      .scope-grid, .metrics, .grid-2, .grid-3 {{
        display: grid;
        gap: 14px;
      }}
      .scope-grid {{ grid-template-columns: repeat(4, minmax(0, 1fr)); margin-bottom: 16px; }}
      .metrics {{ grid-template-columns: repeat(5, minmax(0, 1fr)); margin-bottom: 18px; }}
      .grid-2 {{ grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr); }}
      .grid-3 {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
      .metric-value {{
        font-size: clamp(1.6rem, 3vw, 2.2rem);
        line-height: 1;
        font-weight: 500;
        margin: 8px 0;
      }}
      .metric-label {{ font-weight: 800; }}
      .metric-note {{
        display: inline-block;
        color: #166534;
        background: #dcfce7;
        border-radius: 999px;
        padding: 4px 8px;
        font-size: 0.82rem;
        font-weight: 750;
      }}
      .tabs {{
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        border-bottom: 1px solid var(--line);
        margin-bottom: 20px;
      }}
      .tab {{
        border: 0;
        border-bottom: 3px solid transparent;
        background: transparent;
        padding: 12px 4px 10px;
        color: var(--muted);
        font-weight: 850;
        cursor: pointer;
      }}
      .tab.active {{
        color: var(--green);
        border-bottom-color: var(--green);
      }}
      .tab-pane {{ display: none; }}
      .tab-pane.active {{ display: block; }}
      .chart {{
        width: 100%;
        min-height: 360px;
      }}
      .chart-note {{
        color: var(--muted);
        font-size: 0.9rem;
        margin: 4px 0 12px;
      }}
      table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 0.92rem;
      }}
      th, td {{
        border-bottom: 1px solid var(--line);
        padding: 10px 8px;
        text-align: left;
        vertical-align: top;
      }}
      th {{ color: var(--muted); font-size: 0.82rem; text-transform: uppercase; }}
      .table-wrap {{ overflow-x: auto; }}
      textarea, select {{
        width: 100%;
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 12px;
        font: inherit;
        background: #fff;
      }}
      textarea {{ min-height: 110px; resize: vertical; }}
      .brief-title {{
        font-size: 1.8rem;
        font-weight: 900;
        margin-bottom: 8px;
      }}
      .driver-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 14px 0;
      }}
      .driver-pill {{
        border: 1px solid #cbd5df;
        border-radius: 999px;
        padding: 6px 10px;
        background: #f8fafc;
        font-weight: 800;
      }}
      .button {{
        min-height: 42px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border-radius: 8px;
        padding: 0 14px;
        border: 1px solid var(--green);
        background: var(--green);
        color: #fff;
        text-decoration: none;
        font-weight: 850;
        cursor: pointer;
      }}
      .button.secondary {{ color: var(--green); background: #fff; }}
      .actions {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px; }}
      .footer {{
        color: var(--muted);
        text-align: center;
        padding: 30px 0 0;
      }}
      @media (max-width: 980px) {{
        .hero, .controls, .grid-2, .grid-3, .metrics, .scope-grid {{
          grid-template-columns: 1fr;
        }}
        .nav {{ align-items: flex-start; flex-direction: column; padding: 12px 0; }}
        .hero-main {{ display: block; }}
        .hero-logo {{ margin-bottom: 12px; }}
      }}
    </style>
  </head>
  <body>
    <header class="topbar">
      <nav class="nav">
        <a class="brand" href="index.html">
          <img src="assets/impact_bridge_logo.png" alt="Project logo">
          <span>Sudan Humanitarian AI Insights</span>
        </a>
        <div class="nav-links">
          <a href="index.html">Project Hub</a>
          <a href="downloads/sudan-humanitarian-ai-insights-report.pdf">Report</a>
          <a href="downloads/sudan-humanitarian-ai-insights-carousel.pdf">Carousel</a>
          <a href="https://github.com/Shireenelsabea/shireen-sudan-humanitarian-ai-insights">GitHub</a>
        </div>
      </nav>
    </header>

    <main class="page">
      <section class="hero">
        <div class="panel hero-main">
          <img class="hero-logo" src="assets/impact_bridge_logo.png" alt="Humanitarian AI logo">
          <div>
            <p class="eyebrow">Fully interactive GitHub Pages dashboard</p>
            <h1>Sudan Humanitarian AI Insights</h1>
            <p>
              A privacy-safe dashboard demo that turns synthetic community feedback and public-context
              assumptions into a hotspot watchlist, feedback triage, scenario extension, and downloadable
              decision brief.
            </p>
            <div class="chips">
              <span class="chip">Synthetic demo data</span>
              <span class="chip">No personal data</span>
              <span class="chip">Rule-based text triage</span>
              <span class="chip">Human validation required</span>
            </div>
          </div>
        </div>
        <aside class="panel">
          <h3>Demo Guardrails</h3>
          <div class="guardrail-item"><span class="dot"></span><span>Designed for a LinkedIn case study, not live operational deployment.</span></div>
          <div class="guardrail-item"><span class="dot"></span><span>State values and feedback rows are synthetic scenario data.</span></div>
          <div class="guardrail-item"><span class="dot"></span><span>Priority scores are transparent signals for review, not automated allocation decisions.</span></div>
          <div class="guardrail-item"><span class="dot"></span><span>Public source anchors and ethical-use notes are included in Methodology.</span></div>
        </aside>
      </section>

      <section class="controls">
        <div class="panel">
          <div class="control-title">Region</div>
          <div id="regionFilters" class="check-grid"></div>
        </div>
        <div class="panel">
          <div class="control-title">Priority Level</div>
          <div id="levelFilters" class="check-grid"></div>
        </div>
      </section>

      <section class="scope-grid" id="scopeGrid"></section>
      <section class="metrics" id="metricsGrid"></section>

      <nav class="tabs" aria-label="Dashboard sections">
        <button class="tab active" data-tab="priority">Priority & Needs</button>
        <button class="tab" data-tab="feedback">Feedback Triage</button>
        <button class="tab" data-tab="scenario">Scenario & Actions</button>
        <button class="tab" data-tab="brief">Decision Brief</button>
        <button class="tab" data-tab="methodology">Methodology</button>
      </nav>

      <section id="priority" class="tab-pane active">
        <div class="grid-2">
          <div class="panel">
            <h2>Priority Geography</h2>
            <p class="chart-note">Bubble size shows demo IDP caseload; color shows composite priority score.</p>
            <div id="mapChart" class="chart"></div>
          </div>
          <div class="panel">
            <h2>Top Watchlist</h2>
            <p class="chart-note">Highest scoring states in the current filter selection.</p>
            <div id="priorityBar" class="chart"></div>
          </div>
        </div>
        <div class="panel" style="margin-top:14px">
          <h2>Sector and Access Pressure</h2>
          <p class="chart-note">Percent values are synthetic scenario indicators, not live assessments.</p>
          <div id="heatmapChart" class="chart"></div>
        </div>
        <div class="panel" style="margin-top:14px">
          <h2>State-Level Priority Table</h2>
          <div class="table-wrap" id="stateTable"></div>
        </div>
      </section>

      <section id="feedback" class="tab-pane">
        <div class="metrics" id="feedbackMetrics"></div>
        <div class="grid-2">
          <div class="panel">
            <h2>Predicted Sector Mix</h2>
            <div id="sectorPie" class="chart"></div>
            <h2>Predicted Urgency by Sector</h2>
            <div id="urgencyBar" class="chart"></div>
          </div>
          <div class="panel">
            <h2>Feedback Sample and Rule-Based Tags</h2>
            <div class="table-wrap" id="feedbackTable"></div>
          </div>
        </div>
        <div class="panel" style="margin-top:14px">
          <h2>Test the Rule-Based Classifier</h2>
          <textarea id="classifierInput">The water point is broken and children are sick after using unsafe water.</textarea>
          <div class="metrics" id="classifierMetrics" style="margin:14px 0"></div>
          <div class="panel" id="matchedTerms"></div>
        </div>
      </section>

      <section id="scenario" class="tab-pane">
        <div class="panel">
          <h2>Displacement Trend with Linear Scenario Extension</h2>
          <p class="chart-note">The extension is a simple linear scenario for demonstration, not a predictive model.</p>
          <div id="forecastLine" class="chart"></div>
        </div>
        <div class="grid-2" style="margin-top:14px">
          <div class="panel">
            <h2>Monthly Feedback Pressure by Sector</h2>
            <div id="sectorArea" class="chart"></div>
          </div>
          <div class="panel">
            <h2>Review Queue</h2>
            <div id="actionQueue"></div>
          </div>
        </div>
      </section>

      <section id="brief" class="tab-pane">
        <div class="panel">
          <h2>Decision-Support Brief</h2>
          <p class="chart-note">Select a state to generate a downloadable brief from the same scoring model.</p>
          <select id="briefSelect"></select>
          <div class="grid-2" style="margin-top:14px">
            <div class="panel" id="briefPanel"></div>
            <div class="panel" id="validationPanel"></div>
          </div>
          <h2 style="margin-top:14px">Recommended Review Actions</h2>
          <div class="grid-3" id="reviewActions"></div>
          <h2 style="margin-top:14px">Feedback Signals From This Area</h2>
          <div class="table-wrap" id="briefFeedback"></div>
          <div class="actions">
            <button class="button" id="downloadBrief">Download Selected Brief</button>
          </div>
        </div>
      </section>

      <section id="methodology" class="tab-pane">
        <div class="grid-3">
          <div class="panel"><div class="metric-label">Scenario caseload</div><div class="metric-value">10.8M</div><span class="metric-note">Demo context only</span></div>
          <div class="panel"><div class="metric-label">Feedback privacy</div><div class="metric-value">0 PII</div><span class="metric-note">Synthetic text only</span></div>
          <div class="panel"><div class="metric-label">External cost</div><div class="metric-value">$0</div><span class="metric-note">No paid model or BI license</span></div>
        </div>
        <div class="panel" style="margin-top:14px">
          <h2>Methodology and Ethical Use</h2>
          <p>
            This prototype is designed as a public portfolio demonstration, not an operational deployment.
            State-level values and feedback records are synthetic case-study data calibrated around public
            humanitarian reporting themes. The dashboard does not contain personal data or live field assessments.
          </p>
          <div class="chips">
            <a class="chip" href="https://dtm.iom.int/sudan">IOM DTM Sudan</a>
            <a class="chip" href="https://data.humdata.org/dataset/sdn-iom-dtm-from-api">HDX IOM DTM</a>
            <a class="chip" href="https://data.humdata.org/organization/ocha-sudan">OCHA Sudan HDX</a>
            <a class="chip" href="https://response.reliefweb.int/sudan">ReliefWeb Sudan</a>
          </div>
        </div>
      </section>

      <footer class="footer">
        Created by Shireen Al Sabea. Responsible AI for humanitarian data, MEAL, and community feedback.
      </footer>
    </main>

    <script>
      const DATA = {payload};
      const COLORS = {{
        teal: "#1f7a8c",
        amber: "#c58a20",
        red: "#b42318",
        blue: "#315a8a",
        muted: "#5b6675",
        line: "#d8dee6"
      }};
      const priorityColors = {{ Elevated: COLORS.teal, High: COLORS.amber, Critical: COLORS.red }};
      const state = {{
        regions: [...new Set(DATA.states.map(d => d.region))].sort(),
        levels: ["Critical", "High", "Elevated"],
        activeRegions: new Set(),
        activeLevels: new Set(["Critical", "High", "Elevated"])
      }};
      state.regions.forEach(region => state.activeRegions.add(region));

      function formatInt(value) {{
        const rounded = Math.round(value);
        if (rounded >= 1000000) return (rounded / 1000000).toFixed(1) + "M";
        if (rounded >= 1000) return Math.round(rounded / 1000) + "K";
        return rounded.toLocaleString();
      }}
      function pct(value) {{ return Math.round(value * 100) + "%"; }}
      function filteredStates() {{
        return DATA.states.filter(d => state.activeRegions.has(d.region) && state.activeLevels.has(d.priority_level));
      }}
      function classifyFeedback(text) {{
        const lowered = " " + text.toLowerCase() + " ";
        const scores = {{}};
        Object.entries(DATA.sectorKeywords).forEach(([sector, keywords]) => {{
          scores[sector] = keywords.filter(keyword => lowered.includes(keyword)).length;
        }});
        let topSector = Object.keys(scores).sort((a, b) => scores[b] - scores[a])[0];
        const topScore = scores[topSector];
        if (topScore === 0) topSector = "Unclassified";
        const criticalHits = DATA.criticalTerms.filter(term => lowered.includes(term)).length;
        const urgencyPoints = topScore + criticalHits;
        const urgency = urgencyPoints >= 4 ? "Critical" : urgencyPoints >= 2 ? "High" : "Medium";
        const sentiment = urgency === "Critical" ? "Distress signal" : urgency === "High" ? "Negative" : "Needs follow-up";
        const confidence = Math.min(0.96, 0.48 + topScore * 0.12 + criticalHits * 0.04);
        const matchedTerms = (DATA.sectorKeywords[topSector] || []).filter(keyword => lowered.includes(keyword)).slice(0, 5);
        return {{ sector: topSector, urgency, sentiment, confidence, matchedTerms }};
      }}
      function driverFor(row) {{
        const values = {{
          food_insecurity_pct: row.food_insecurity_pct,
          wash_gap_pct: row.wash_gap_pct,
          health_gap_pct: row.health_gap_pct,
          access_constraint: row.access_constraint,
          protection_alerts: row.protection_pressure,
          funding_gap_pct: row.funding_gap_pct
        }};
        return Object.keys(values).sort((a, b) => values[b] - values[a])[0];
      }}
      function hotspotDrivers(row) {{
        const items = [
          {{ key: "idp_pressure", label: DATA.driverLabels.idp_pressure, score: Math.min(row.idps / 1600000, 1), display: formatInt(row.idps) + " IDPs" }},
          {{ key: "food_insecurity_pct", label: DATA.driverLabels.food_insecurity_pct, score: row.food_insecurity_pct, display: pct(row.food_insecurity_pct) }},
          {{ key: "wash_gap_pct", label: DATA.driverLabels.wash_gap_pct, score: row.wash_gap_pct, display: pct(row.wash_gap_pct) }},
          {{ key: "health_gap_pct", label: DATA.driverLabels.health_gap_pct, score: row.health_gap_pct, display: pct(row.health_gap_pct) }},
          {{ key: "access_constraint", label: DATA.driverLabels.access_constraint, score: row.access_constraint, display: pct(row.access_constraint) }},
          {{ key: "protection_alerts", label: DATA.driverLabels.protection_alerts, score: row.protection_pressure, display: row.protection_alerts + " alerts" }},
          {{ key: "funding_gap_pct", label: DATA.driverLabels.funding_gap_pct, score: row.funding_gap_pct, display: pct(row.funding_gap_pct) }}
        ];
        return items.sort((a, b) => b.score - a.score);
      }}
      function card(label, value, note) {{
        return `<div class="panel"><div class="metric-label">${{label}}</div><div class="metric-value">${{value}}</div><span class="metric-note">${{note}}</span></div>`;
      }}
      function renderFilters() {{
        document.getElementById("regionFilters").innerHTML = state.regions.map(region => `
          <label class="check"><input type="checkbox" data-region="${{region}}" checked> ${{region}}</label>
        `).join("");
        document.getElementById("levelFilters").innerHTML = state.levels.map(level => `
          <label class="check"><input type="checkbox" data-level="${{level}}" checked> ${{level}}</label>
        `).join("");
        document.querySelectorAll("[data-region]").forEach(input => input.addEventListener("change", e => {{
          e.target.checked ? state.activeRegions.add(e.target.dataset.region) : state.activeRegions.delete(e.target.dataset.region);
          renderAll();
        }}));
        document.querySelectorAll("[data-level]").forEach(input => input.addEventListener("change", e => {{
          e.target.checked ? state.activeLevels.add(e.target.dataset.level) : state.activeLevels.delete(e.target.dataset.level);
          renderAll();
        }}));
      }}
      function renderScope() {{
        const latest = new Date(DATA.trends[DATA.trends.length - 1].month).toLocaleString("en", {{ month: "short", year: "numeric" }});
        document.getElementById("scopeGrid").innerHTML = [
          card("18 states", "18", "Synthetic priority rows"),
          card("30 messages", "30", "Synthetic feedback samples"),
          card("Latest observed month", latest, "Before scenario extension"),
          card("Decision posture", "Human review", "Validation required")
        ].join("");
      }}
      function renderMetrics(rows) {{
        if (!rows.length) {{
          document.getElementById("metricsGrid").innerHTML = card("No matches", "0", "Adjust filters");
          return;
        }}
        const total = rows.reduce((sum, row) => sum + row.idps, 0);
        const children = rows.reduce((sum, row) => sum + row.children_estimate, 0);
        const avg = rows.reduce((sum, row) => sum + row.priority_score, 0) / rows.length;
        const critical = rows.filter(row => row.priority_level === "Critical").length;
        const top = [...rows].sort((a, b) => b.priority_score - a.priority_score)[0];
        document.getElementById("metricsGrid").innerHTML = [
          card("Demo IDP caseload", formatInt(total), rows.length + " states in scope"),
          card("Estimated children", formatInt(children), Math.round(children / total * 100) + "% derived share"),
          card("Mean priority score", avg.toFixed(1) + "/100", "Composite model"),
          card("Critical watchlist", critical, "Review first"),
          card("Highest ranked state", top.state, "By demo priority score")
        ].join("");
      }}
      function plotPriority(rows) {{
        const layoutBase = {{
          margin: {{ l: 10, r: 10, t: 10, b: 20 }},
          paper_bgcolor: "rgba(0,0,0,0)",
          plot_bgcolor: "rgba(0,0,0,0)",
          font: {{ color: "#17202a" }}
        }};
        Plotly.newPlot("mapChart", [{{
          type: "scatter",
          mode: "markers+text",
          x: rows.map(d => d.lon),
          y: rows.map(d => d.lat),
          text: rows.map(d => d.state),
          textposition: "top center",
          marker: {{
            size: rows.map(d => Math.max(10, Math.sqrt(d.idps) / 35)),
            color: rows.map(d => d.priority_score),
            colorscale: [[0, COLORS.teal], [0.55, COLORS.amber], [1, COLORS.red]],
            showscale: true,
            colorbar: {{ title: "Priority" }},
            line: {{ color: "#fff", width: 1 }}
          }},
          hovertemplate: "%{{text}}<br>IDPs: %{{customdata[0]:,}}<br>Score: %{{customdata[1]}}<extra></extra>",
          customdata: rows.map(d => [d.idps, d.priority_score])
        }}], {{
          ...layoutBase,
          height: 430,
          xaxis: {{ title: "Longitude", range: [20, 39], gridcolor: "#e6edf3" }},
          yaxis: {{ title: "Latitude", range: [7, 23], gridcolor: "#e6edf3" }}
        }}, {{ responsive: true, displayModeBar: false }});

        const top = [...rows].sort((a, b) => a.priority_score - b.priority_score).slice(-10);
        Plotly.newPlot("priorityBar", [{{
          type: "bar",
          orientation: "h",
          x: top.map(d => d.priority_score),
          y: top.map(d => d.state),
          marker: {{ color: top.map(d => priorityColors[d.priority_level]) }},
          text: top.map(d => d.priority_score),
          textposition: "outside",
          hovertemplate: "%{{y}}<br>Score: %{{x}}<extra></extra>"
        }}], {{
          ...layoutBase,
          height: 430,
          xaxis: {{ range: [0, 100], title: "Priority score", gridcolor: "#e6edf3" }},
          yaxis: {{ automargin: true }}
        }}, {{ responsive: true, displayModeBar: false }});

        const heatRows = [...rows].sort((a, b) => b.priority_score - a.priority_score).slice(0, 10);
        const columns = ["food_insecurity_pct", "wash_gap_pct", "health_gap_pct", "access_constraint", "funding_gap_pct"];
        Plotly.newPlot("heatmapChart", [{{
          type: "heatmap",
          z: heatRows.map(row => columns.map(col => Math.round(row[col] * 100))),
          x: columns.map(col => DATA.driverLabels[col]),
          y: heatRows.map(row => row.state),
          colorscale: [[0, "#e6eef2"], [0.55, COLORS.amber], [1, COLORS.red]],
          colorbar: {{ title: "Gap" }},
          hovertemplate: "%{{y}}<br>%{{x}}: %{{z}}%<extra></extra>"
        }}], {{ ...layoutBase, height: 420, yaxis: {{ automargin: true }} }}, {{ responsive: true, displayModeBar: false }});
      }}
      function renderStateTable(rows) {{
        const sorted = [...rows].sort((a, b) => b.priority_score - a.priority_score);
        document.getElementById("stateTable").innerHTML = `<table><thead><tr>
          <th>State</th><th>Region</th><th>Priority</th><th>Score</th><th>IDPs</th><th>Children</th><th>Food</th><th>WASH</th><th>Health</th><th>Access</th>
        </tr></thead><tbody>${{sorted.map(row => `<tr>
          <td>${{row.state}}</td><td>${{row.region}}</td><td>${{row.priority_level}}</td><td>${{row.priority_score}}</td>
          <td>${{formatInt(row.idps)}}</td><td>${{formatInt(row.children_estimate)}}</td>
          <td>${{pct(row.food_insecurity_pct)}}</td><td>${{pct(row.wash_gap_pct)}}</td><td>${{pct(row.health_gap_pct)}}</td><td>${{pct(row.access_constraint)}}</td>
        </tr>`).join("")}}</tbody></table>`;
      }}
      function renderFeedback() {{
        const matchRate = DATA.feedback.filter(row => row.match).length / DATA.feedback.length;
        const critical = DATA.feedback.filter(row => row.ai_urgency === "Critical").length;
        document.getElementById("feedbackMetrics").innerHTML = [
          card("Feedback records", DATA.feedback.length, "Synthetic sample"),
          card("Rule match rate", Math.round(matchRate * 100) + "%", "Against demo labels"),
          card("Critical signals", critical, "Predicted urgency"),
          card("States represented", new Set(DATA.feedback.map(row => row.state)).size, "Across Sudan")
        ].join("");
        const sectorCounts = Object.entries(DATA.feedback.reduce((acc, row) => {{
          acc[row.ai_sector] = (acc[row.ai_sector] || 0) + 1;
          return acc;
        }}, {{}}));
        Plotly.newPlot("sectorPie", [{{
          type: "pie",
          labels: sectorCounts.map(([key]) => key),
          values: sectorCounts.map(([, value]) => value),
          hole: 0.52,
          marker: {{ colors: [COLORS.teal, COLORS.amber, COLORS.red, COLORS.blue, "#6b7280", "#7c5c2e"] }}
        }}], {{ height: 330, margin: {{ l: 10, r: 10, t: 10, b: 10 }}, paper_bgcolor: "rgba(0,0,0,0)" }}, {{ responsive: true, displayModeBar: false }});
        const sectors = [...new Set(DATA.feedback.map(row => row.ai_sector))];
        const urgencies = ["Critical", "High", "Medium"];
        Plotly.newPlot("urgencyBar", urgencies.map(urgency => ({{
          type: "bar",
          name: urgency,
          x: sectors,
          y: sectors.map(sector => DATA.feedback.filter(row => row.ai_sector === sector && row.ai_urgency === urgency).length),
          marker: {{ color: urgency === "Critical" ? COLORS.red : urgency === "High" ? COLORS.amber : COLORS.teal }}
        }})), {{
          barmode: "stack",
          height: 330,
          margin: {{ l: 40, r: 10, t: 10, b: 90 }},
          paper_bgcolor: "rgba(0,0,0,0)",
          plot_bgcolor: "rgba(0,0,0,0)",
          yaxis: {{ title: "Records", gridcolor: "#e6edf3" }}
        }}, {{ responsive: true, displayModeBar: false }});
        const rows = [...DATA.feedback].sort((a, b) => b.date.localeCompare(a.date));
        document.getElementById("feedbackTable").innerHTML = `<table><thead><tr><th>Date</th><th>State</th><th>Message</th><th>Predicted sector</th><th>Urgency</th><th>Confidence</th></tr></thead><tbody>${{rows.map(row => `<tr><td>${{row.date}}</td><td>${{row.state}}</td><td>${{row.message}}</td><td>${{row.ai_sector}}</td><td>${{row.ai_urgency}}</td><td>${{Math.round(row.confidence * 100)}}%</td></tr>`).join("")}}</tbody></table>`;
        renderClassifier();
      }}
      function renderClassifier() {{
        const result = classifyFeedback(document.getElementById("classifierInput").value);
        document.getElementById("classifierMetrics").innerHTML = [
          card("Sector", result.sector, "Rule output"),
          card("Urgency", result.urgency, "Triage level"),
          card("Sentiment", result.sentiment, "Signal"),
          card("Confidence", Math.round(result.confidence * 100) + "%", "Rule confidence")
        ].join("");
        document.getElementById("matchedTerms").innerHTML = `<div class="metric-label">Matched terms</div><p>${{result.matchedTerms.length ? result.matchedTerms.join(", ") : "No strong sector terms found"}}</p>`;
      }}
      function renderScenario(rows) {{
        const series = [...new Set(DATA.forecast.map(row => row.series))];
        Plotly.newPlot("forecastLine", series.map(name => {{
          const vals = DATA.forecast.filter(row => row.series === name);
          return {{
            type: "scatter",
            mode: "lines+markers",
            name,
            x: vals.map(row => row.month),
            y: vals.map(row => row.total_idps),
            line: {{ color: name === "Observed" ? COLORS.teal : COLORS.red, width: 3 }}
          }};
        }}), {{
          height: 380,
          margin: {{ l: 60, r: 10, t: 10, b: 50 }},
          paper_bgcolor: "rgba(0,0,0,0)",
          plot_bgcolor: "rgba(0,0,0,0)",
          yaxis: {{ title: "Estimated IDPs", gridcolor: "#e6edf3" }}
        }}, {{ responsive: true, displayModeBar: false }});
        const sectorColumns = ["food_reports", "wash_reports", "health_reports", "shelter_reports", "protection_reports"];
        Plotly.newPlot("sectorArea", sectorColumns.map((col, idx) => ({{
          type: "scatter",
          mode: "lines",
          stackgroup: "one",
          name: col.replace("_reports", "").replace("_", " ").replace(/\\b\\w/g, c => c.toUpperCase()),
          x: DATA.trends.map(row => row.month),
          y: DATA.trends.map(row => row[col]),
          line: {{ color: [COLORS.teal, COLORS.blue, COLORS.amber, "#7c5c2e", COLORS.red][idx] }}
        }})), {{
          height: 430,
          margin: {{ l: 50, r: 10, t: 10, b: 50 }},
          paper_bgcolor: "rgba(0,0,0,0)",
          plot_bgcolor: "rgba(0,0,0,0)",
          yaxis: {{ title: "Monthly records", gridcolor: "#e6edf3" }}
        }}, {{ responsive: true, displayModeBar: false }});
        const queue = [...rows].sort((a, b) => b.priority_score - a.priority_score).slice(0, 6);
        document.getElementById("actionQueue").innerHTML = queue.map(row => {{
          const key = driverFor(row);
          return `<div class="panel" style="margin-bottom:10px;border-left:5px solid ${{priorityColors[row.priority_level]}}">
            <strong>${{row.state}}</strong> - ${{row.priority_level}} - Score ${{row.priority_score}}
            <p>Driver: ${{DATA.driverLabels[key]}} | Caseload: ${{formatInt(row.idps)}}</p>
            <p>${{DATA.recommendations[key]}}</p>
          </div>`;
        }}).join("");
      }}
      function buildBrief(row) {{
        const drivers = hotspotDrivers(row);
        const related = DATA.feedback.filter(item => item.state === row.state);
        const lines = [
          `Decision-Support Brief: ${{row.state}}`,
          `Priority: ${{row.priority_level}} | Score: ${{row.priority_score}}/100`,
          `Estimated IDPs: ${{formatInt(row.idps)}} | Children estimate: ${{formatInt(row.children_estimate)}}`,
          "",
          "Why this hotspot matters:",
          "The dashboard ranks this area using displacement volume, sector gaps, access constraints, protection alerts, and funding pressure.",
          "Top drivers: " + drivers.slice(0, 4).map(driver => `${{driver.label}} (${{driver.display}})`).join("; "),
          "",
          "Recommended moves:",
          ...drivers.slice(0, 3).map(driver => "- " + DATA.recommendations[driver.key]),
          "",
          "Feedback signals:",
          related.length ? related.map(item => `- ${{item.date}} | ${{item.ai_sector}} | ${{item.ai_urgency}} | ${{item.message}}`).join("\\n") : "No synthetic feedback records attached.",
          "",
          "Field validation steps:",
          ...DATA.validationSteps[row.priority_level].map(step => "- " + step),
          "",
          "Ethical note:",
          "This is a decision-support brief. It should guide human review, not replace field validation or community accountability."
        ];
        return lines.join("\\n");
      }}
      function renderBriefOptions(rows) {{
        const select = document.getElementById("briefSelect");
        const sorted = [...rows].sort((a, b) => b.priority_score - a.priority_score);
        select.innerHTML = sorted.map(row => `<option value="${{row.state}}">${{row.state}}</option>`).join("");
        select.onchange = () => renderBrief();
        renderBrief();
      }}
      function renderBrief() {{
        const selected = document.getElementById("briefSelect").value || DATA.states[0].state;
        const row = DATA.states.find(item => item.state === selected);
        const drivers = hotspotDrivers(row);
        const driverHtml = drivers.slice(0, 5).map(driver => `<span class="driver-pill">${{driver.label}}: ${{driver.display}}</span>`).join("");
        document.getElementById("briefPanel").innerHTML = `<div class="brief-title">${{row.state}}</div><p>${{row.state}} is marked as ${{row.priority_level}} because the composite score combines large displacement volume, sector pressure, protection alerts, access constraints, and funding gaps.</p><div class="driver-row">${{driverHtml}}</div><h3>Recommended response posture</h3><p>Treat this hotspot as a decision-support signal. Use it to prioritize field validation, coordination, and resource planning before any final allocation decision.</p>`;
        document.getElementById("validationPanel").innerHTML = `<h3>Validation Steps</h3>${{DATA.validationSteps[row.priority_level].map(step => `<div class="panel" style="margin-bottom:8px;border-left:4px solid var(--teal)">${{step}}</div>`).join("")}}`;
        document.getElementById("reviewActions").innerHTML = drivers.slice(0, 3).map(driver => `<div class="panel"><div class="metric-label">${{driver.label}}</div><p>${{DATA.recommendations[driver.key]}}</p></div>`).join("");
        const related = DATA.feedback.filter(item => item.state === row.state).sort((a, b) => b.date.localeCompare(a.date));
        document.getElementById("briefFeedback").innerHTML = related.length ? `<table><thead><tr><th>Date</th><th>Channel</th><th>Message</th><th>Sector</th><th>Urgency</th></tr></thead><tbody>${{related.map(item => `<tr><td>${{item.date}}</td><td>${{item.channel}}</td><td>${{item.message}}</td><td>${{item.ai_sector}}</td><td>${{item.ai_urgency}}</td></tr>`).join("")}}</tbody></table>` : `<p>No synthetic feedback records are attached to this state in the current demo sample.</p>`;
      }}
      function renderAll() {{
        const rows = filteredStates();
        renderScope();
        renderMetrics(rows);
        plotPriority(rows);
        renderStateTable(rows);
        renderFeedback();
        renderScenario(rows);
        renderBriefOptions(rows.length ? rows : DATA.states);
      }}
      document.querySelectorAll(".tab").forEach(button => {{
        button.addEventListener("click", () => {{
          document.querySelectorAll(".tab").forEach(tab => tab.classList.remove("active"));
          document.querySelectorAll(".tab-pane").forEach(pane => pane.classList.remove("active"));
          button.classList.add("active");
          document.getElementById(button.dataset.tab).classList.add("active");
          window.dispatchEvent(new Event("resize"));
        }});
      }});
      document.getElementById("classifierInput").addEventListener("input", renderClassifier);
      document.getElementById("downloadBrief").addEventListener("click", () => {{
        const selected = document.getElementById("briefSelect").value || DATA.states[0].state;
        const row = DATA.states.find(item => item.state === selected);
        const blob = new Blob([buildBrief(row)], {{ type: "text/plain" }});
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = selected.toLowerCase().replaceAll(" ", "_") + "_decision_brief.txt";
        link.click();
        URL.revokeObjectURL(url);
      }});
      renderFilters();
      renderAll();
    </script>
  </body>
</html>
"""


def main() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / "dashboard.html").write_text(build_html(), encoding="utf-8")


if __name__ == "__main__":
    main()
