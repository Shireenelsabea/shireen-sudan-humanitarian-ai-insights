from __future__ import annotations

import base64
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ASSET_DIR = ROOT / "assets"
LOGO_PATH = ASSET_DIR / "impact_bridge_logo.png"
CREATOR_NAME = "Shireen El Sabea"
CREATOR_LINKEDIN = "https://www.linkedin.com/in/shireenalsabea/"
CREATOR_EMAIL = "sabeashireen@gmail.com"

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


st.set_page_config(
    page_title="Sudan Humanitarian AI Insights",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def apply_theme() -> None:
    st.markdown(
        """
        <style>
            :root {
                --ink: #17202a;
                --muted: #5b6675;
                --line: #d8dee6;
                --paper: #ffffff;
                --canvas: #f5f7f9;
                --green: #1f6f5b;
                --teal: #1f7a8c;
                --amber: #c58a20;
                --coral: #b42318;
                --blue: #315a8a;
            }

            .stApp {
                background: var(--canvas);
                color: var(--ink);
            }

            .block-container {
                padding-top: 1rem;
                padding-bottom: 2.5rem;
                max-width: 1440px;
            }

            .stDeployButton,
            [data-testid="stToolbar"],
            #MainMenu,
            footer {
                display: none;
            }

            header[data-testid="stHeader"] {
                height: 0;
                background: transparent;
            }

            [data-testid="stSidebar"] {
                background: #f0f4f7;
                border-right: 1px solid var(--line);
            }

            h1, h2, h3 {
                color: var(--ink);
                letter-spacing: 0;
            }

            .eyebrow {
                color: var(--green);
                font-size: 0.78rem;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 0;
                margin-bottom: 0.2rem;
            }

            .hero {
                border: 1px solid var(--line);
                border-radius: 6px;
                padding: 1.2rem 1.25rem;
                background: #ffffff;
                margin-bottom: 1rem;
                box-shadow: 0 14px 34px rgba(23, 32, 42, 0.05);
            }

            .hero-grid {
                display: grid;
                grid-template-columns: minmax(0, 1.35fr) minmax(280px, 0.65fr);
                gap: 1rem;
                align-items: stretch;
            }

            .brand-row {
                display: flex;
                gap: 0.75rem;
                align-items: center;
                margin-bottom: 0.5rem;
            }

            .hero-logo {
                width: 58px;
                height: 58px;
                border-radius: 10px;
                object-fit: cover;
                border: 1px solid #d8dee6;
                background: #ffffff;
            }

            .hero h1 {
                margin: 0 0 0.25rem 0;
                font-size: clamp(1.9rem, 3.2vw, 2.75rem);
                line-height: 1.08;
            }

            .hero p {
                margin: 0.25rem 0 0 0;
                color: var(--muted);
                font-size: 1rem;
                max-width: 980px;
            }

            .badge-row {
                display: flex;
                gap: 0.45rem;
                flex-wrap: wrap;
                margin-top: 0.85rem;
            }

            .badge {
                border: 1px solid #cbd5df;
                border-radius: 999px;
                padding: 0.24rem 0.62rem;
                background: #f7fafc;
                color: var(--ink);
                font-size: 0.82rem;
                font-weight: 650;
            }

            .creator-line {
                color: var(--ink);
                font-size: 0.95rem;
                margin-top: 0.65rem;
            }

            .hero-media {
                border: 1px solid #d9e5df;
                border-radius: 6px;
                overflow: hidden;
                background: #ffffff;
                box-shadow: 0 18px 42px rgba(23, 33, 28, 0.07);
            }

            .logo-reveal {
                display: block;
                width: 100%;
                aspect-ratio: 16 / 9;
                object-fit: cover;
                background: #ffffff;
            }

            .media-caption {
                display: flex;
                justify-content: space-between;
                gap: 0.65rem;
                align-items: center;
                padding: 0.55rem 0.75rem;
                color: var(--muted);
                font-size: 0.82rem;
                border-top: 1px solid var(--line);
            }

            .brand-mini {
                color: var(--muted);
                font-size: 0.9rem;
                font-weight: 700;
            }

            .guardrail-panel {
                height: 100%;
                border: 1px solid #d8dee6;
                border-radius: 6px;
                background: #f8fafc;
                padding: 0.9rem 0.95rem;
            }

            .guardrail-title {
                color: var(--ink);
                font-size: 0.95rem;
                font-weight: 800;
                margin-bottom: 0.6rem;
            }

            .guardrail-item {
                display: flex;
                gap: 0.55rem;
                align-items: flex-start;
                color: var(--muted);
                font-size: 0.9rem;
                line-height: 1.35;
                margin-bottom: 0.55rem;
            }

            .status-dot {
                width: 8px;
                height: 8px;
                border-radius: 999px;
                margin-top: 0.35rem;
                background: var(--green);
                flex: 0 0 auto;
            }

            .scope-strip {
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: 0.7rem;
                margin: 0.75rem 0 1rem 0;
            }

            .scope-item {
                border: 1px solid var(--line);
                border-radius: 6px;
                background: var(--paper);
                padding: 0.75rem 0.85rem;
                min-height: 86px;
            }

            .scope-value {
                color: var(--ink);
                font-size: 1rem;
                font-weight: 800;
                margin-bottom: 0.2rem;
            }

            .scope-label {
                color: var(--muted);
                font-size: 0.86rem;
                line-height: 1.35;
            }

            .section-kicker {
                color: var(--muted);
                font-size: 0.88rem;
                margin: -0.2rem 0 0.7rem 0;
            }

            .chart-note {
                color: var(--muted);
                font-size: 0.86rem;
                margin: -0.25rem 0 0.7rem 0;
            }

            @media (max-width: 980px) {
                .hero-grid {
                    grid-template-columns: 1fr;
                }

                .scope-strip {
                    grid-template-columns: repeat(2, minmax(0, 1fr));
                }
            }

            @media (max-width: 640px) {
                .scope-strip {
                    grid-template-columns: 1fr;
                }
            }

            div[data-testid="stMetric"] {
                background: var(--paper);
                border: 1px solid var(--line);
                border-radius: 6px;
                padding: 0.85rem 0.95rem;
                min-height: 106px;
                box-shadow: 0 8px 24px rgba(23, 32, 42, 0.04);
            }

            div[data-testid="stMetricLabel"] p {
                color: var(--muted);
                font-weight: 700;
            }

            div[data-testid="stMetricValue"] {
                font-size: clamp(1.7rem, 2.2vw, 2.15rem);
                white-space: normal;
                overflow-wrap: anywhere;
            }

            div[data-testid="stMetricDelta"] {
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                max-width: 100%;
            }

            .custom-metric {
                background: var(--paper);
                border: 1px solid var(--line);
                border-radius: 6px;
                padding: 0.85rem 0.95rem;
                min-height: 106px;
            }

            .custom-metric-label {
                color: var(--muted);
                font-size: 0.88rem;
                font-weight: 700;
                margin-bottom: 0.25rem;
            }

            .custom-metric-value {
                color: var(--ink);
                font-size: clamp(1.35rem, 1.9vw, 1.85rem);
                line-height: 1.15;
                margin-bottom: 0.45rem;
            }

            .custom-metric-delta {
                display: inline-block;
                color: #166534;
                background: #dcfce7;
                border-radius: 999px;
                padding: 0.1rem 0.45rem;
                font-size: 0.82rem;
                max-width: 100%;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }

            .section-card {
                background: var(--paper);
                border: 1px solid var(--line);
                border-radius: 6px;
                padding: 1rem;
            }

            .action-card {
                border: 1px solid var(--line);
                border-left: 5px solid var(--coral);
                border-radius: 6px;
                padding: 0.9rem 1rem;
                background: var(--paper);
                margin-bottom: 0.75rem;
            }

            .action-card strong {
                color: var(--ink);
            }

            .action-meta {
                color: var(--muted);
                font-size: 0.86rem;
                margin-top: 0.25rem;
            }

            .mini-label {
                color: var(--muted);
                font-size: 0.82rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0;
            }

            .result-box {
                border: 1px solid #cfdcd6;
                border-radius: 6px;
                padding: 0.95rem;
                background: #fbfcf9;
            }

            .brief-panel {
                border: 1px solid var(--line);
                border-radius: 6px;
                padding: 1rem;
                background: var(--paper);
            }

            .brief-title {
                font-size: 1.45rem;
                font-weight: 800;
                margin-bottom: 0.25rem;
                color: var(--ink);
            }

            .brief-text {
                color: var(--muted);
                margin-bottom: 0.8rem;
            }

            .driver-row {
                display: flex;
                gap: 0.45rem;
                flex-wrap: wrap;
                margin: 0.65rem 0 0.85rem 0;
            }

            .driver-pill {
                border: 1px solid #d4dfd9;
                border-radius: 999px;
                padding: 0.22rem 0.55rem;
                font-size: 0.82rem;
                background: #f9fbf8;
                color: var(--ink);
                font-weight: 650;
            }

            .step-card {
                border-left: 4px solid var(--teal);
                background: #f8fbf8;
                padding: 0.75rem 0.85rem;
                border-radius: 4px;
                margin-bottom: 0.55rem;
            }

            .cta-strip {
                border: 1px solid #cfded7;
                border-radius: 6px;
                padding: 1rem;
                background: #ffffff;
                margin-top: 0.85rem;
            }

            .cta-strip strong {
                color: var(--ink);
            }

            .footer-note {
                color: var(--muted);
                font-size: 0.9rem;
            }

            button[kind="secondary"] {
                border-radius: 6px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    states = pd.read_csv(DATA_DIR / "state_needs.csv")
    trends = pd.read_csv(DATA_DIR / "monthly_trends.csv", parse_dates=["month"])
    feedback = pd.read_csv(DATA_DIR / "feedback_samples.csv", parse_dates=["date"])
    return score_states(states), trends, feedback


@st.cache_data
def asset_data_uri(path: Path, mime_type: str) -> str:
    if not path.exists():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


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


def format_int(value: float | int) -> str:
    value = int(round(value))
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.0f}K"
    return f"{value:,}"


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
        "confidence": confidence,
        "matched_terms": matched_terms,
        "sector_scores": sector_scores,
    }


def normalized_sector(value: str) -> str:
    if value == "Child Protection":
        return "Protection"
    return value


def enrich_feedback(feedback: pd.DataFrame) -> pd.DataFrame:
    enriched = feedback.copy()
    results = enriched["message"].apply(classify_feedback)
    enriched["ai_sector"] = results.apply(lambda item: item["sector"])
    enriched["ai_urgency"] = results.apply(lambda item: item["urgency"])
    enriched["confidence"] = results.apply(lambda item: round(item["confidence"], 2))
    enriched["match"] = enriched.apply(
        lambda row: normalized_sector(row["sector"]) == normalized_sector(row["ai_sector"]),
        axis=1,
    )
    return enriched


def make_forecast(trends: pd.DataFrame, months: int = 3) -> pd.DataFrame:
    actual = trends[["month", "total_idps"]].copy()
    actual["series"] = "Observed"

    x = np.arange(len(actual))
    y = actual["total_idps"].to_numpy()
    slope, intercept = np.polyfit(x, y, 1)
    future_x = np.arange(len(actual), len(actual) + months)
    last_month = actual["month"].max()
    future_months = pd.date_range(last_month + pd.offsets.MonthBegin(1), periods=months, freq="MS")

    forecast = pd.DataFrame(
        {
            "month": future_months,
            "total_idps": np.round(slope * future_x + intercept).astype(int),
            "series": "Linear scenario extension",
        }
    )
    return pd.concat([actual, forecast], ignore_index=True)


def driver_for(row: pd.Series) -> tuple[str, str]:
    driver_values = {
        "food_insecurity_pct": row["food_insecurity_pct"],
        "wash_gap_pct": row["wash_gap_pct"],
        "health_gap_pct": row["health_gap_pct"],
        "access_constraint": row["access_constraint"],
        "protection_alerts": row["protection_pressure"],
        "funding_gap_pct": row["funding_gap_pct"],
    }
    key = max(driver_values, key=driver_values.get)
    return key, DRIVER_LABELS[key]


def build_action_queue(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in df.nlargest(6, "priority_score").iterrows():
        driver_key, driver_label = driver_for(row)
        rows.append(
            {
                "State": row["state"],
                "Priority": row["priority_level"],
                "Score": row["priority_score"],
                "Primary driver": driver_label,
                "Recommended move": RECOMMENDATIONS[driver_key],
                "Estimated IDPs": row["idps"],
            }
        )
    return pd.DataFrame(rows)


def hotspot_drivers(row: pd.Series) -> list[dict[str, object]]:
    values = [
        {
            "key": "idp_pressure",
            "label": DRIVER_LABELS["idp_pressure"],
            "score": min(float(row["idps"]) / 1_600_000, 1.0),
            "display": f"{format_int(row['idps'])} IDPs",
        },
        {
            "key": "food_insecurity_pct",
            "label": DRIVER_LABELS["food_insecurity_pct"],
            "score": float(row["food_insecurity_pct"]),
            "display": f"{row['food_insecurity_pct']:.0%}",
        },
        {
            "key": "wash_gap_pct",
            "label": DRIVER_LABELS["wash_gap_pct"],
            "score": float(row["wash_gap_pct"]),
            "display": f"{row['wash_gap_pct']:.0%}",
        },
        {
            "key": "health_gap_pct",
            "label": DRIVER_LABELS["health_gap_pct"],
            "score": float(row["health_gap_pct"]),
            "display": f"{row['health_gap_pct']:.0%}",
        },
        {
            "key": "access_constraint",
            "label": DRIVER_LABELS["access_constraint"],
            "score": float(row["access_constraint"]),
            "display": f"{row['access_constraint']:.0%}",
        },
        {
            "key": "protection_alerts",
            "label": DRIVER_LABELS["protection_alerts"],
            "score": float(row["protection_pressure"]),
            "display": f"{int(row['protection_alerts'])} alerts",
        },
        {
            "key": "funding_gap_pct",
            "label": DRIVER_LABELS["funding_gap_pct"],
            "score": float(row["funding_gap_pct"]),
            "display": f"{row['funding_gap_pct']:.0%}",
        },
    ]
    return sorted(values, key=lambda item: float(item["score"]), reverse=True)


def build_hotspot_brief_text(row: pd.Series, drivers: list[dict[str, object]], feedback_rows: pd.DataFrame) -> str:
    level = str(row["priority_level"])
    validation_steps = VALIDATION_STEPS.get(level, VALIDATION_STEPS["Elevated"])
    actions = [RECOMMENDATIONS[str(driver["key"])] for driver in drivers[:3]]
    feedback_summary = "No synthetic community feedback is attached to this state in the demo sample."
    if not feedback_rows.empty:
        sectors = feedback_rows["ai_sector"].value_counts().head(3)
        feedback_summary = ", ".join(f"{sector}: {count}" for sector, count in sectors.items())

    return "\n".join(
        [
            f"Decision-Support Brief: {row['state']}",
            f"Priority: {level} | Score: {row['priority_score']:.1f}/100",
            f"Estimated IDPs: {format_int(row['idps'])} | Children estimate: {format_int(row['children_estimate'])}",
            "",
            "Why this hotspot matters:",
            "The dashboard ranks this area using a transparent demo score: displacement volume, sector gaps, access constraints, protection alerts, and funding pressure.",
            "Top drivers: " + "; ".join(f"{driver['label']} ({driver['display']})" for driver in drivers[:4]),
            "",
            "Recommended moves:",
            *[f"- {action}" for action in actions],
            "",
            "Feedback signals:",
            feedback_summary,
            "",
            "Field validation steps:",
            *[f"- {step}" for step in validation_steps],
            "",
            "Ethical note:",
            "This is a decision-support brief. It should guide human review, not replace field validation or community accountability.",
            "",
            "Demo note:",
            "This brief was generated from synthetic case-study data for portfolio demonstration and discussion.",
        ]
    )


def plot_map(df: pd.DataFrame) -> go.Figure:
    fig = px.scatter_geo(
        df,
        lat="lat",
        lon="lon",
        size="idps",
        color="priority_score",
        hover_name="state",
        hover_data={
            "region": True,
            "priority_level": True,
            "idps": ":,",
            "children_estimate": ":,",
            "lat": False,
            "lon": False,
        },
        color_continuous_scale=["#1f7a8c", "#c58a20", "#b42318"],
        size_max=44,
        projection="natural earth",
    )
    fig.update_geos(
        showcountries=True,
        countrycolor="#9aa9a1",
        showland=True,
        landcolor="#edf1ea",
        showocean=True,
        oceancolor="#edf7f7",
        lataxis_range=[7, 23],
        lonaxis_range=[20, 39],
        resolution=50,
    )
    fig.update_layout(
        height=520,
        margin=dict(l=0, r=0, t=8, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_colorbar=dict(title="Priority"),
    )
    return fig


def plot_priority_bar(df: pd.DataFrame) -> go.Figure:
    top = df.nlargest(10, "priority_score").sort_values("priority_score")
    fig = px.bar(
        top,
        x="priority_score",
        y="state",
        orientation="h",
        color="priority_level",
        color_discrete_map={
            "Critical": "#b42318",
            "High": "#c58a20",
            "Elevated": "#1f7a8c",
        },
        text="priority_score",
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(
        height=360,
        xaxis_title="Priority score",
        yaxis_title=None,
        margin=dict(l=0, r=20, t=8, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend_title=None,
        xaxis_range=[0, 100],
    )
    return fig


def plot_sector_heatmap(df: pd.DataFrame) -> go.Figure:
    heat = df.nlargest(10, "priority_score").copy()
    columns = [
        "food_insecurity_pct",
        "wash_gap_pct",
        "health_gap_pct",
        "access_constraint",
        "funding_gap_pct",
    ]
    z = (heat[columns] * 100).round(0).to_numpy()
    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=[DRIVER_LABELS[col] for col in columns],
            y=heat["state"],
            colorscale=[[0, "#e6eef2"], [0.55, "#c58a20"], [1, "#b42318"]],
            hovertemplate="%{y}<br>%{x}: %{z:.0f}%<extra></extra>",
            colorbar=dict(title="Gap"),
        )
    )
    fig.update_layout(
        height=360,
        margin=dict(l=0, r=0, t=8, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def render_header() -> None:
    logo_uri = asset_data_uri(LOGO_PATH, "image/png")
    logo_html = f'<img class="hero-logo" src="{logo_uri}" alt="Humanitarian AI logo">' if logo_uri else ""

    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-grid">
                <div>
                    <div class="brand-row">
                        {logo_html}
                        <div>
                            <div class="eyebrow">Public portfolio prototype</div>
                            <div class="brand-mini">Humanitarian needs analysis with transparent scoring</div>
                        </div>
                    </div>
                    <h1>Sudan Humanitarian AI Insights</h1>
                    <p>
                        A privacy-safe dashboard demo that turns synthetic community feedback and
                        public-context assumptions into a hotspot watchlist, feedback triage, scenario
                        extension, and downloadable decision brief.
                    </p>
                    <p class="creator-line">
                        Created by <strong>{CREATOR_NAME}</strong> for humanitarian data analysis,
                        responsible AI, and social-impact collaboration.
                    </p>
                    <div class="badge-row">
                        <span class="badge">Synthetic demo data</span>
                        <span class="badge">No personal data</span>
                        <span class="badge">Rule-based text triage</span>
                        <span class="badge">Human validation required</span>
                    </div>
                </div>
                <div class="guardrail-panel">
                    <div class="guardrail-title">Demo Guardrails</div>
                    <div class="guardrail-item"><span class="status-dot"></span><span>Designed for a LinkedIn case study, not live operational deployment.</span></div>
                    <div class="guardrail-item"><span class="status-dot"></span><span>State values and feedback rows are synthetic and should be read as scenario data.</span></div>
                    <div class="guardrail-item"><span class="status-dot"></span><span>Priority scores are transparent signals for review, not automated allocation decisions.</span></div>
                    <div class="guardrail-item"><span class="status-dot"></span><span>Public source anchors and ethics notes are documented in Methodology Notes.</span></div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    contact_1, contact_2 = st.columns([0.34, 0.66])
    contact_1.link_button("LinkedIn Profile", CREATOR_LINKEDIN, width="stretch")
    contact_2.link_button(
        "Reach Shireen for Collaboration",
        f"mailto:{CREATOR_EMAIL}?subject=Collaboration%20on%20Humanitarian%20AI%20Dashboard",
        width="stretch",
    )


def render_demo_scope(states: pd.DataFrame, trends: pd.DataFrame, feedback_ai: pd.DataFrame) -> None:
    latest_month = trends["month"].max().strftime("%b %Y")
    st.markdown(
        f"""
        <div class="scope-strip">
            <div class="scope-item">
                <div class="scope-value">{len(states)} states</div>
                <div class="scope-label">Synthetic state-level rows used for the priority model.</div>
            </div>
            <div class="scope-item">
                <div class="scope-value">{len(feedback_ai)} messages</div>
                <div class="scope-label">Synthetic feedback samples for local text triage.</div>
            </div>
            <div class="scope-item">
                <div class="scope-value">{latest_month}</div>
                <div class="scope-label">Last observed month before the simple scenario extension.</div>
            </div>
            <div class="scope-item">
                <div class="scope-value">Human review</div>
                <div class="scope-label">The dashboard supports validation, coordination, and planning.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metrics(df: pd.DataFrame) -> None:
    total_idps = df["idps"].sum()
    children = df["children_estimate"].sum()
    avg_priority = df["priority_score"].mean()
    critical_count = (df["priority_level"] == "Critical").sum()
    top_state = df.sort_values("priority_score", ascending=False).iloc[0]["state"]

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Demo IDP caseload", format_int(total_idps), f"{len(df)} states in scope")
    col2.metric("Estimated children", format_int(children), f"{children / total_idps:.0%} derived share")
    col3.metric("Mean priority score", f"{avg_priority:.1f}/100", "Composite model")
    col4.metric("Critical watchlist", f"{critical_count}", "Review first")
    col5.markdown(
        f"""
        <div class="custom-metric">
            <div class="custom-metric-label">Highest ranked state</div>
            <div class="custom-metric-value">{top_state}</div>
            <div class="custom-metric-delta">By demo priority score</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_action_cards(queue: pd.DataFrame) -> None:
    for _, row in queue.iterrows():
        st.markdown(
            f"""
            <div class="action-card">
                <strong>{row["State"]}</strong> &middot; {row["Priority"]} &middot; Score {row["Score"]:.1f}
                <div class="action-meta">Driver: {row["Primary driver"]} &middot; Caseload: {format_int(row["Estimated IDPs"])}</div>
                <div style="margin-top:0.55rem;">{row["Recommended move"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_hotspot_brief(df: pd.DataFrame, feedback_ai: pd.DataFrame) -> None:
    ordered = df.sort_values("priority_score", ascending=False)
    selected_state = st.selectbox(
        "Select a hotspot to brief",
        ordered["state"].tolist(),
        index=0,
        key="hotspot_brief_state",
    )
    row = ordered.loc[ordered["state"] == selected_state].iloc[0]
    related_feedback = feedback_ai.loc[feedback_ai["state"] == selected_state].copy()
    drivers = hotspot_drivers(row)
    brief_text = build_hotspot_brief_text(row, drivers, related_feedback)
    validation_steps = VALIDATION_STEPS.get(str(row["priority_level"]), VALIDATION_STEPS["Elevated"])

    st.markdown("#### Decision-Support Brief")
    top_line = (
        f"{row['state']} is marked as {row['priority_level']} because the composite score combines "
        f"large displacement volume, sector pressure, protection alerts, access constraints, and funding gaps."
    )
    driver_html = "".join(
        f'<span class="driver-pill">{driver["label"]}: {driver["display"]}</span>'
        for driver in drivers[:5]
    )

    brief_col, action_col = st.columns([1.2, 0.8])
    with brief_col:
        st.markdown(
            f"""
            <div class="brief-panel">
                <div class="brief-title">{row["state"]}</div>
                <div class="brief-text">{top_line}</div>
                <div class="driver-row">{driver_html}</div>
                <div class="mini-label">Recommended response posture</div>
                <p>
                    Treat this hotspot as a decision-support signal. Use it to prioritize field validation,
                    coordination, and resource planning before any final allocation decision.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.download_button(
            "Download selected hotspot brief",
            data=brief_text,
            file_name=f"{selected_state.lower().replace(' ', '_')}_decision_brief.txt",
            mime="text/plain",
        )

    with action_col:
        m1, m2 = st.columns(2)
        m1.metric("Priority score", f"{row['priority_score']:.1f}/100", row["priority_level"])
        m2.metric("Estimated IDPs", format_int(row["idps"]), f"{format_int(row['children_estimate'])} children")
        st.markdown("##### Validation Steps")
        for step in validation_steps:
            st.markdown(f'<div class="step-card">{step}</div>', unsafe_allow_html=True)

    st.markdown("#### Recommended Review Actions")
    action_1, action_2, action_3 = st.columns(3)
    for column, driver in zip([action_1, action_2, action_3], drivers[:3]):
        with column:
            st.markdown(
                f"""
                <div class="brief-panel">
                    <div class="mini-label">{driver["label"]}</div>
                    <p>{RECOMMENDATIONS[str(driver["key"])]}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("#### Feedback Signals From This Area")
    if related_feedback.empty:
        st.info("No synthetic feedback records are attached to this state in the current demo sample.")
    else:
        st.dataframe(
            related_feedback[["date", "channel", "message", "ai_sector", "ai_urgency", "confidence"]]
            .assign(confidence=lambda data: (data["confidence"] * 100).round(0).astype(int))
            .sort_values("date", ascending=False),
            width="stretch",
            hide_index=True,
            column_config={
                "date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
                "channel": "Channel",
                "message": "Synthetic feedback",
                "ai_sector": "Predicted sector",
                "ai_urgency": "Predicted urgency",
                "confidence": st.column_config.ProgressColumn("Confidence", min_value=0, max_value=100, format="%d%%"),
            },
        )

    render_cta_strip()


def render_cta_strip() -> None:
    st.markdown(
        f"""
        <div class="cta-strip">
            <strong>Creator and collaboration:</strong>
            This prototype was created by <strong>{CREATOR_NAME}</strong>. She is open to collaboration with
            humanitarian organizations, data teams, and social-impact employers working on responsible AI for
            needs analysis, community feedback, and decision-support workflows.
            <br>
            <strong>LinkedIn:</strong> <a href="{CREATOR_LINKEDIN}" target="_blank">{CREATOR_LINKEDIN}</a>
            <br>
            <strong>Email:</strong> <a href="mailto:{CREATOR_EMAIL}">{CREATOR_EMAIL}</a>
        </div>
        """,
        unsafe_allow_html=True,
    )
    cta_1, cta_2 = st.columns(2)
    cta_1.link_button("Connect on LinkedIn", CREATOR_LINKEDIN, width="stretch")
    cta_2.link_button(
        "Reach Shireen for Collaboration",
        f"mailto:{CREATOR_EMAIL}?subject=Collaboration%20on%20Humanitarian%20AI%20Dashboard",
        width="stretch",
    )


def main() -> None:
    apply_theme()
    states, trends, feedback = load_data()
    feedback_ai = enrich_feedback(feedback)

    if LOGO_PATH.exists():
        st.sidebar.image(str(LOGO_PATH), width=128)
    st.sidebar.markdown("### Sudan AI Insights")
    st.sidebar.caption(f"Portfolio prototype by {CREATOR_NAME}.")
    st.sidebar.link_button("LinkedIn Profile", CREATOR_LINKEDIN, width="stretch")
    st.sidebar.link_button(
        "Email",
        f"mailto:{CREATOR_EMAIL}?subject=Collaboration%20on%20Humanitarian%20AI%20Dashboard",
        width="stretch",
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Demo Controls")
    region_filter = st.sidebar.multiselect(
        "Region",
        sorted(states["region"].unique()),
        default=sorted(states["region"].unique()),
    )
    level_filter = st.sidebar.multiselect(
        "Priority level",
        ["Critical", "High", "Elevated"],
        default=["Critical", "High", "Elevated"],
    )
    st.sidebar.info("Demo data only. Use Methodology Notes for public context and ethical-use caveats.")

    filtered = states[
        states["region"].isin(region_filter) & states["priority_level"].isin(level_filter)
    ].copy()

    render_header()
    render_demo_scope(states, trends, feedback_ai)

    if filtered.empty:
        st.warning("No states match the current filters.")
        return

    render_metrics(filtered)

    overview_tab, feedback_tab, forecast_tab, brief_tab, notes_tab = st.tabs(
        ["Priority & Needs", "Feedback Triage", "Scenario & Actions", "Decision Brief", "Methodology Notes"]
    )

    with overview_tab:
        left, right = st.columns([1.35, 1])
        with left:
            st.markdown("#### Priority Geography")
            st.markdown(
                '<div class="chart-note">Bubble size shows demo IDP caseload; color shows composite priority score.</div>',
                unsafe_allow_html=True,
            )
            st.plotly_chart(plot_map(filtered), width="stretch")
        with right:
            st.markdown("#### Top Watchlist")
            st.markdown(
                '<div class="chart-note">Highest scoring states in the current filter selection.</div>',
                unsafe_allow_html=True,
            )
            st.plotly_chart(plot_priority_bar(filtered), width="stretch")

        st.markdown("#### Sector and Access Pressure")
        st.markdown(
            '<div class="chart-note">Percent values are synthetic scenario indicators, not live assessments.</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(plot_sector_heatmap(filtered), width="stretch")

        percent_columns = [
            "food_insecurity_pct",
            "wash_gap_pct",
            "health_gap_pct",
            "access_constraint",
        ]
        display_states = filtered.sort_values("priority_score", ascending=False).copy()
        display_states[percent_columns] = (display_states[percent_columns] * 100).round(0).astype(int)
        st.markdown("#### State-Level Priority Table")
        st.dataframe(
            display_states[
                [
                    "state",
                    "region",
                    "priority_level",
                    "priority_score",
                    "idps",
                    "children_estimate",
                    "food_insecurity_pct",
                    "wash_gap_pct",
                    "health_gap_pct",
                    "access_constraint",
                ]
            ],
            width="stretch",
            hide_index=True,
            column_config={
                "state": "State",
                "region": "Region",
                "priority_level": "Priority",
                "priority_score": st.column_config.NumberColumn("Score", format="%.1f"),
                "idps": st.column_config.NumberColumn("IDPs", format="%d"),
                "children_estimate": st.column_config.NumberColumn("Children estimate", format="%d"),
                "food_insecurity_pct": st.column_config.ProgressColumn("Food gap", format="%d%%", min_value=0, max_value=100),
                "wash_gap_pct": st.column_config.ProgressColumn("WASH gap", format="%d%%", min_value=0, max_value=100),
                "health_gap_pct": st.column_config.ProgressColumn("Health gap", format="%d%%", min_value=0, max_value=100),
                "access_constraint": st.column_config.ProgressColumn("Access constraint", format="%d%%", min_value=0, max_value=100),
            },
        )

    with feedback_tab:
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        match_rate = feedback_ai["match"].mean()
        critical_feedback = (feedback_ai["ai_urgency"] == "Critical").sum()
        kpi1.metric("Feedback records", f"{len(feedback_ai)}", "Synthetic sample")
        kpi2.metric("Rule match rate", f"{match_rate:.0%}", "Against demo labels")
        kpi3.metric("Critical signals", f"{critical_feedback}", "Predicted urgency")
        kpi4.metric("States represented", feedback_ai["state"].nunique(), "Across Sudan")

        chart_col, table_col = st.columns([0.9, 1.25])
        with chart_col:
            sector_counts = feedback_ai["ai_sector"].value_counts().reset_index()
            sector_counts.columns = ["sector", "count"]
            fig = px.pie(
                sector_counts,
                names="sector",
                values="count",
                hole=0.52,
                color_discrete_sequence=["#1f7a8c", "#c58a20", "#b42318", "#315a8a", "#6b7280", "#7c5c2e"],
            )
            fig.update_layout(
                title="Predicted Sector Mix",
                height=360,
                margin=dict(l=0, r=0, t=45, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig, width="stretch")

            urgency_order = ["Critical", "High", "Medium"]
            urgency_counts = (
                feedback_ai.groupby(["ai_sector", "ai_urgency"])
                .size()
                .reset_index(name="count")
            )
            fig2 = px.bar(
                urgency_counts,
                x="ai_sector",
                y="count",
                color="ai_urgency",
                category_orders={"ai_urgency": urgency_order},
                color_discrete_map={"Critical": "#b42318", "High": "#c58a20", "Medium": "#1f7a8c"},
            )
            fig2.update_layout(
                title="Predicted Urgency by Sector",
                xaxis_title=None,
                yaxis_title="Records",
                height=310,
                margin=dict(l=0, r=0, t=45, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                legend_title=None,
            )
            st.plotly_chart(fig2, width="stretch")

        with table_col:
            st.markdown("#### Feedback Sample and Rule-Based Tags")
            display_feedback = feedback_ai[
                [
                    "date",
                    "state",
                    "channel",
                    "message",
                    "sector",
                    "urgency",
                    "ai_sector",
                    "ai_urgency",
                    "confidence",
                ]
            ].sort_values("date", ascending=False)
            display_feedback = display_feedback.assign(
                confidence=(display_feedback["confidence"] * 100).round(0).astype(int)
            )
            st.dataframe(
                display_feedback,
                width="stretch",
                hide_index=True,
                height=520,
                column_config={
                    "date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
                    "state": "State",
                    "channel": "Channel",
                    "message": "Feedback",
                    "sector": "Demo label",
                    "urgency": "Demo urgency",
                    "ai_sector": "Predicted sector",
                    "ai_urgency": "Predicted urgency",
                    "confidence": st.column_config.ProgressColumn("Rule confidence", min_value=0, max_value=100, format="%d%%"),
                },
            )

        st.markdown("#### Test the Rule-Based Classifier")
        sample = st.text_area(
            "Community feedback sample",
            value="The water point is broken and children are sick after using unsafe water.",
            height=100,
        )
        result = classify_feedback(sample)
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Sector", result["sector"])
        r2.metric("Urgency", result["urgency"])
        r3.metric("Sentiment", result["sentiment"])
        r4.metric("Rule confidence", f"{result['confidence']:.0%}")
        st.markdown(
            f"""
            <div class="result-box">
                <div class="mini-label">Matched terms</div>
                {", ".join(result["matched_terms"]) if result["matched_terms"] else "No strong sector terms found"}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with forecast_tab:
        forecast = make_forecast(trends)
        forecast_fig = px.line(
            forecast,
            x="month",
            y="total_idps",
            color="series",
            markers=True,
            color_discrete_map={"Observed": "#1f7a8c", "Linear scenario extension": "#b42318"},
        )
        forecast_fig.update_traces(line=dict(width=3))
        forecast_fig.update_layout(
            title="Displacement Trend with Linear Scenario Extension",
            yaxis_title="Estimated IDPs",
            xaxis_title=None,
            height=390,
            margin=dict(l=0, r=0, t=45, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend_title=None,
        )
        st.plotly_chart(forecast_fig, width="stretch")
        st.markdown(
            '<div class="chart-note">The extension is a simple linear scenario for demonstration, not a predictive model.</div>',
            unsafe_allow_html=True,
        )

        sector_long = trends.melt(
            id_vars=["month"],
            value_vars=[
                "food_reports",
                "wash_reports",
                "health_reports",
                "shelter_reports",
                "protection_reports",
            ],
            var_name="sector",
            value_name="reports",
        )
        sector_long["sector"] = (
            sector_long["sector"]
            .str.replace("_reports", "", regex=False)
            .str.replace("_", " ")
            .str.title()
        )
        left, right = st.columns([1.1, 0.9])
        with left:
            sector_fig = px.area(
                sector_long,
                x="month",
                y="reports",
                color="sector",
                color_discrete_sequence=["#1f7a8c", "#315a8a", "#c58a20", "#7c5c2e", "#b42318"],
            )
            sector_fig.update_layout(
                title="Monthly Feedback Pressure by Sector",
                xaxis_title=None,
                yaxis_title="Monthly records",
                height=430,
                margin=dict(l=0, r=0, t=45, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                legend_title=None,
            )
            st.plotly_chart(sector_fig, width="stretch")

        with right:
            st.markdown("#### Review Queue")
            render_action_cards(build_action_queue(filtered))

    with brief_tab:
        render_hotspot_brief(filtered, feedback_ai)

    with notes_tab:
        st.markdown("#### Methodology and Ethical Use")
        n1, n2, n3 = st.columns(3)
        n1.metric("Scenario caseload", "10.8M", "Demo context only")
        n2.metric("Feedback privacy", "0 PII", "Synthetic text only")
        n3.metric("External cost", "$0", "No paid model or BI license")

        st.markdown(
            """
            This prototype is designed as a public portfolio demonstration, not an operational deployment.
            State-level values and feedback records are synthetic case-study data calibrated around public
            humanitarian reporting themes. The dashboard does not contain personal data or live field assessments.

            Public sources that can be cited for context when writing about the case study:

            - IOM DTM Sudan Mobility Tracking: https://dtm.iom.int/sudan
            - HDX Sudan IOM DTM dataset page: https://data.humdata.org/dataset/sdn-iom-dtm-from-api
            - OCHA Sudan Humanitarian Response Plan / HDX context: https://data.humdata.org/organization/ocha-sudan
            - ReliefWeb Sudan response updates: https://response.reliefweb.int/sudan
            """,
        )

        st.markdown(
            """
            #### LinkedIn Positioning
            Use this as a visual proof-of-concept: useful humanitarian AI can start with transparent
            data preparation, clear assumptions, and human review. The value is not automatic decision-making;
            it is faster triage, better documentation, and a more structured conversation about priorities.
            """
        )

        render_cta_strip()

        st.markdown(
            """
            <p class="footer-note">
                Ethical guardrail: this dashboard supports human decision-making. It should not replace
                field validation, protection protocols, or community accountability mechanisms.
            </p>
            """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
