from __future__ import annotations

import base64
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components


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
    initial_sidebar_state="expanded",
)


def apply_theme() -> None:
    st.markdown(
        """
        <style>
            :root {
                --ink: #17211c;
                --muted: #5f6f67;
                --line: #dce4de;
                --paper: #ffffff;
                --canvas: #f6f7f3;
                --green: #2d6a4f;
                --teal: #287271;
                --amber: #e9c46a;
                --coral: #c44536;
                --violet: #6d597a;
            }

            .stApp {
                background: var(--canvas);
                color: var(--ink);
            }

            .block-container {
                padding-top: 0.75rem;
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
                background: #eef3ee;
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
                margin-bottom: 0.15rem;
            }

            .hero {
                border: 1px solid var(--line);
                border-radius: 6px;
                padding: 1.15rem 1.25rem;
                background: linear-gradient(120deg, #ffffff 0%, #f4f0e9 58%, #eef6f5 100%);
                margin-bottom: 0.9rem;
            }

            .hero-grid {
                display: grid;
                grid-template-columns: minmax(0, 1.25fr) minmax(280px, 0.75fr);
                gap: 1rem;
                align-items: center;
            }

            .brand-row {
                display: flex;
                gap: 0.75rem;
                align-items: center;
                margin-bottom: 0.5rem;
            }

            .hero-logo {
                width: 68px;
                height: 68px;
                border-radius: 12px;
                object-fit: cover;
                border: 1px solid #d8e3de;
                background: #ffffff;
            }

            .hero h1 {
                margin: 0 0 0.25rem 0;
                font-size: clamp(2rem, 4vw, 3.25rem);
                line-height: 1.05;
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
                margin-top: 0.8rem;
            }

            .badge {
                border: 1px solid #cbd8d1;
                border-radius: 999px;
                padding: 0.22rem 0.62rem;
                background: rgba(255, 255, 255, 0.72);
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
                color: var(--green);
                font-weight: 800;
            }

            @media (max-width: 980px) {
                .hero-grid {
                    grid-template-columns: 1fr;
                }

                .hero-media {
                    max-width: 560px;
                }
            }

            div[data-testid="stMetric"] {
                background: var(--paper);
                border: 1px solid var(--line);
                border-radius: 6px;
                padding: 0.85rem 0.95rem;
                min-height: 106px;
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
                color: #000000;
                font-size: clamp(1.35rem, 1.9vw, 1.85rem);
                line-height: 1.15;
                margin-bottom: 0.45rem;
            }

            .custom-metric-delta {
                display: inline-block;
                color: #087f3c;
                background: #dff4e7;
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
                background: linear-gradient(100deg, #ffffff 0%, #eef7f4 52%, #fff5e8 100%);
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
            "series": "Scenario forecast",
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
            f"AI Action Brief: {row['state']}",
            f"Priority: {level} | Score: {row['priority_score']:.1f}/100",
            f"Estimated IDPs: {format_int(row['idps'])} | Children estimate: {format_int(row['children_estimate'])}",
            "",
            "Why this hotspot matters:",
            "The dashboard ranks this area based on displacement volume, sector gaps, access constraints, protection alerts, and funding pressure.",
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
            "CTA:",
            "Use this prototype to discuss partnerships with NGOs, humanitarian data teams, and social-impact employers interested in responsible AI.",
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
        color_continuous_scale=["#287271", "#e9c46a", "#c44536"],
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
            "Critical": "#c44536",
            "High": "#e9c46a",
            "Elevated": "#287271",
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
            colorscale=[[0, "#e8f1ed"], [0.55, "#e9c46a"], [1, "#c44536"]],
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

    with st.container(border=True):
        copy_col, media_col = st.columns([1.45, 0.75], vertical_alignment="center")
        with copy_col:
            st.markdown(
                f"""
                <div class="brand-row">
                    {logo_html}
                    <div>
                        <div class="eyebrow">Humanitarian intelligence demo</div>
                        <div class="brand-mini">AI for accountable crisis response</div>
                    </div>
                </div>
                <h1>Sudan Humanitarian AI Insights</h1>
                <p>
                    A branded first-phase prototype showing how public crisis context and privacy-safe synthetic
                    feedback can become rapid operational insight for NGO teams, donors, and social-impact employers.
                </p>
                <p class="creator-line">
                    Created by <strong>{CREATOR_NAME}</strong> for humanitarian AI, data analysis, and social-impact collaboration.
                </p>
                <div class="badge-row">
                    <span class="badge">No paid APIs</span>
                    <span class="badge">Local NLP scoring</span>
                    <span class="badge">AI action briefs</span>
                    <span class="badge">Deployment-ready assets</span>
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
        with media_col:
            if logo_uri:
                components.html(
                    f"""
                    <style>
                        body {{
                            margin: 0;
                            background: transparent;
                            font-family: Arial, sans-serif;
                        }}
                        .reveal-shell {{
                            border: 1px solid #d9e5df;
                            border-radius: 8px;
                            overflow: hidden;
                            background: #ffffff;
                            box-shadow: 0 14px 34px rgba(23, 33, 28, 0.08);
                        }}
                        .stage {{
                            position: relative;
                            height: 190px;
                            display: grid;
                            place-items: center;
                            overflow: hidden;
                            background:
                                radial-gradient(circle at 20% 30%, rgba(0, 138, 208, 0.14), transparent 24%),
                                radial-gradient(circle at 82% 42%, rgba(255, 111, 0, 0.16), transparent 25%),
                                linear-gradient(135deg, #ffffff 0%, #f7fbfb 100%);
                        }}
                        .stage::before {{
                            content: "";
                            position: absolute;
                            inset: -20%;
                            background:
                                linear-gradient(110deg, transparent 0%, rgba(255,255,255,0.85) 45%, rgba(255,255,255,0.2) 54%, transparent 70%);
                            transform: translateX(-100%) rotate(8deg);
                            animation: sweep 3.8s ease-in-out infinite;
                        }}
                        .logo {{
                            position: relative;
                            width: min(68%, 230px);
                            filter: drop-shadow(0 14px 24px rgba(23, 33, 28, 0.12));
                            animation: reveal 3.8s ease-in-out infinite;
                        }}
                        .ring {{
                            position: absolute;
                            width: 78%;
                            max-width: 260px;
                            aspect-ratio: 1;
                            border: 1px solid rgba(45,106,79,0.18);
                            border-radius: 50%;
                            animation: pulse 3.8s ease-in-out infinite;
                        }}
                        .dot {{
                            position: absolute;
                            width: 7px;
                            height: 7px;
                            border-radius: 50%;
                            background: #0b74ba;
                            box-shadow: 0 0 0 5px rgba(11,116,186,0.08);
                            animation: float 4.8s ease-in-out infinite;
                        }}
                        .dot.orange {{
                            background: #f97316;
                            box-shadow: 0 0 0 5px rgba(249,115,22,0.10);
                        }}
                        .d1 {{ left: 18%; top: 30%; }}
                        .d2 {{ left: 76%; top: 28%; animation-delay: 0.4s; }}
                        .d3 {{ left: 68%; top: 74%; animation-delay: 0.8s; }}
                        .d4 {{ left: 25%; top: 72%; animation-delay: 1.2s; }}
                        .caption {{
                            color: #5f6f67;
                            font-size: 13px;
                            padding: 10px 12px;
                            border-top: 1px solid #dce4de;
                            display: flex;
                            justify-content: space-between;
                            gap: 10px;
                        }}
                        @keyframes reveal {{
                            0% {{ opacity: 0.7; transform: scale(0.96); }}
                            42% {{ opacity: 1; transform: scale(1.02); }}
                            100% {{ opacity: 0.92; transform: scale(1); }}
                        }}
                        @keyframes sweep {{
                            0% {{ transform: translateX(-115%) rotate(8deg); }}
                            48% {{ transform: translateX(115%) rotate(8deg); }}
                            100% {{ transform: translateX(115%) rotate(8deg); }}
                        }}
                        @keyframes pulse {{
                            0% {{ opacity: 0.25; transform: scale(0.95); }}
                            45% {{ opacity: 0.72; transform: scale(1.04); }}
                            100% {{ opacity: 0.3; transform: scale(1); }}
                        }}
                        @keyframes float {{
                            0%, 100% {{ transform: translateY(0); }}
                            50% {{ transform: translateY(-9px); }}
                        }}
                    </style>
                    <div class="reveal-shell">
                        <div class="stage">
                            <div class="ring"></div>
                            <span class="dot d1"></span>
                            <span class="dot orange d2"></span>
                            <span class="dot d3"></span>
                            <span class="dot orange d4"></span>
                            <img class="logo" src="{logo_uri}" alt="{CREATOR_NAME} humanitarian AI logo">
                        </div>
                        <div class="caption">
                            <span>Clean logo reveal</span>
                            <span>Portfolio-ready deployment</span>
                        </div>
                    </div>
                    """,
                    height=260,
                )


def render_metrics(df: pd.DataFrame) -> None:
    total_idps = df["idps"].sum()
    children = df["children_estimate"].sum()
    avg_priority = df["priority_score"].mean()
    critical_count = (df["priority_level"] == "Critical").sum()
    top_state = df.sort_values("priority_score", ascending=False).iloc[0]["state"]

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Estimated IDPs", format_int(total_idps), f"{len(df)} states")
    col2.metric("Children estimate", format_int(children), f"{children / total_idps:.0%} of caseload")
    col3.metric("Average priority", f"{avg_priority:.1f}/100", "Transparent scoring")
    col4.metric("Critical states", f"{critical_count}", "Immediate review")
    col5.markdown(
        f"""
        <div class="custom-metric">
            <div class="custom-metric-label">Top hotspot</div>
            <div class="custom-metric-value">{top_state}</div>
            <div class="custom-metric-delta">Highest composite score</div>
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

    st.markdown("#### AI Action Brief")
    top_line = (
        f"{row['state']} is marked as {row['priority_level']} because the composite model combines "
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
                    coordination, and resource planning before final allocation.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.download_button(
            "Download selected hotspot brief",
            data=brief_text,
            file_name=f"{selected_state.lower().replace(' ', '_')}_ai_action_brief.txt",
            mime="text/plain",
        )

    with action_col:
        m1, m2 = st.columns(2)
        m1.metric("Priority score", f"{row['priority_score']:.1f}/100", row["priority_level"])
        m2.metric("Estimated IDPs", format_int(row["idps"]), f"{format_int(row['children_estimate'])} children")
        st.markdown("##### Next Steps")
        for step in validation_steps:
            st.markdown(f'<div class="step-card">{step}</div>', unsafe_allow_html=True)

    st.markdown("#### What To Do With This Spot")
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
                "ai_sector": "AI sector",
                "ai_urgency": "AI urgency",
                "confidence": st.column_config.ProgressColumn("Confidence", min_value=0, max_value=100, format="%d%%"),
            },
        )

    render_cta_strip()


def render_cta_strip() -> None:
    st.markdown(
        f"""
        <div class="cta-strip">
            <strong>CTA for employers and NGO partners:</strong>
            This platform was created by <strong>{CREATOR_NAME}</strong>. She is open to collaboration with
            humanitarian organizations, data teams, and social-impact employers interested in responsible AI for
            needs analysis, community feedback, and decision-support dashboards.
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
    st.sidebar.markdown("### AI Humanitarian Insights")
    st.sidebar.caption(f"Created by {CREATOR_NAME}.")
    st.sidebar.link_button("LinkedIn Profile", CREATOR_LINKEDIN, width="stretch")
    st.sidebar.link_button(
        "Collaboration Email",
        f"mailto:{CREATOR_EMAIL}?subject=Collaboration%20on%20Humanitarian%20AI%20Dashboard",
        width="stretch",
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Filters")
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

    filtered = states[
        states["region"].isin(region_filter) & states["priority_level"].isin(level_filter)
    ].copy()

    render_header()

    if filtered.empty:
        st.warning("No states match the current filters.")
        return

    render_metrics(filtered)

    overview_tab, feedback_tab, forecast_tab, brief_tab, notes_tab = st.tabs(
        ["Operations View", "Feedback Intelligence", "Forecast & Actions", "Hotspot Brief", "Data Notes"]
    )

    with overview_tab:
        left, right = st.columns([1.35, 1])
        with left:
            st.markdown("#### Geographic Priority")
            st.plotly_chart(plot_map(filtered), width="stretch")
        with right:
            st.markdown("#### Ranked Hotspots")
            st.plotly_chart(plot_priority_bar(filtered), width="stretch")

        st.markdown("#### Sector Pressure Matrix")
        st.plotly_chart(plot_sector_heatmap(filtered), width="stretch")

        percent_columns = [
            "food_insecurity_pct",
            "wash_gap_pct",
            "health_gap_pct",
            "access_constraint",
        ]
        display_states = filtered.sort_values("priority_score", ascending=False).copy()
        display_states[percent_columns] = (display_states[percent_columns] * 100).round(0).astype(int)
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
                "food_insecurity_pct": st.column_config.ProgressColumn("Food", format="%d%%", min_value=0, max_value=100),
                "wash_gap_pct": st.column_config.ProgressColumn("WASH", format="%d%%", min_value=0, max_value=100),
                "health_gap_pct": st.column_config.ProgressColumn("Health", format="%d%%", min_value=0, max_value=100),
                "access_constraint": st.column_config.ProgressColumn("Access", format="%d%%", min_value=0, max_value=100),
            },
        )

    with feedback_tab:
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        match_rate = feedback_ai["match"].mean()
        critical_feedback = (feedback_ai["urgency"] == "Critical").sum()
        kpi1.metric("Feedback records", f"{len(feedback_ai)}", "Synthetic sample")
        kpi2.metric("Local NLP match", f"{match_rate:.0%}", "Baseline classifier")
        kpi3.metric("Critical signals", f"{critical_feedback}", "Immediate triage")
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
                color_discrete_sequence=["#287271", "#e9c46a", "#c44536", "#6d597a", "#4f7cac", "#d88c4a"],
            )
            fig.update_layout(
                title="Classified Feedback by Sector",
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
                color_discrete_map={"Critical": "#c44536", "High": "#e9c46a", "Medium": "#287271"},
            )
            fig2.update_layout(
                title="Urgency Signals",
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
            st.markdown("#### Synthetic Community Feedback")
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
                    "sector": "Human label",
                    "urgency": "Human urgency",
                    "ai_sector": "AI sector",
                    "ai_urgency": "AI urgency",
                    "confidence": st.column_config.ProgressColumn("Confidence", min_value=0, max_value=100, format="%d%%"),
                },
            )

        st.markdown("#### Live Local Classifier")
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
        r4.metric("Confidence", f"{result['confidence']:.0%}")
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
            color_discrete_map={"Observed": "#287271", "Scenario forecast": "#c44536"},
        )
        forecast_fig.update_traces(line=dict(width=3))
        forecast_fig.update_layout(
            title="Displacement Trend and Scenario Forecast",
            yaxis_title="Estimated IDPs",
            xaxis_title=None,
            height=390,
            margin=dict(l=0, r=0, t=45, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend_title=None,
        )
        st.plotly_chart(forecast_fig, width="stretch")

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
                color_discrete_sequence=["#287271", "#4f7cac", "#e9c46a", "#d88c4a", "#c44536"],
            )
            sector_fig.update_layout(
                title="Feedback Pressure by Sector",
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
            st.markdown("#### Intervention Queue")
            render_action_cards(build_action_queue(filtered))

    with brief_tab:
        render_hotspot_brief(filtered, feedback_ai)

    with notes_tab:
        st.markdown("#### Public Context Anchors")
        n1, n2, n3 = st.columns(3)
        n1.metric("Reference caseload", "10.8M", "IOM DTM public context")
        n2.metric("Feedback privacy", "0 PII", "Synthetic text only")
        n3.metric("External cost", "$0", "No paid model or BI license")

        st.markdown(
            """
            This prototype is designed as a first public demonstration, not an operational deployment.
            State-level values and feedback records are synthetic demonstration data calibrated around public
            humanitarian reporting themes. No personal data is included.

            Public sources to reference in the case study:

            - IOM DTM Sudan Mobility Tracking: https://dtm.iom.int/sudan
            - HDX Sudan IOM DTM dataset page: https://data.humdata.org/dataset/sdn-iom-dtm-from-api
            - OCHA Sudan Humanitarian Response Plan / HDX context: https://data.humdata.org/organization/ocha-sudan
            - ReliefWeb Sudan response updates: https://response.reliefweb.int/sudan
            """,
        )

        st.markdown(
            """
            #### LinkedIn Positioning
            Use this as a visual proof-of-concept: AI does not need to begin with expensive infrastructure.
            Even a lightweight local model can classify community feedback, surface hotspots, and help teams
            discuss prioritization with more evidence and transparency.
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
