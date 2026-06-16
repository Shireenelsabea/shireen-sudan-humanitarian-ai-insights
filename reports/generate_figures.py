from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
FIG_DIR = ROOT / "reports" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

GREEN = "#2d6a4f"
TEAL = "#287271"
AMBER = "#e9c46a"
CORAL = "#c44536"
BLUE = "#4f7cac"
ORANGE = "#f97316"
MUTED = "#5f6f67"
PAPER = "#ffffff"


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


def save(fig: plt.Figure, filename: str) -> None:
    fig.savefig(FIG_DIR / filename, dpi=220, bbox_inches="tight", facecolor=PAPER)
    plt.close(fig)


def priority_bar(states: pd.DataFrame) -> None:
    top = states.nlargest(10, "priority_score").sort_values("priority_score")
    colors = top["priority_level"].map(
        {"Critical": CORAL, "High": AMBER, "Elevated": TEAL}
    )
    fig, ax = plt.subplots(figsize=(8.6, 5.2))
    ax.barh(top["state"], top["priority_score"], color=colors)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Composite priority score")
    ax.set_title("Top 10 Hotspots by Priority Score", loc="left", color=GREEN, weight="bold")
    ax.grid(axis="x", alpha=0.2)
    for y, value in enumerate(top["priority_score"]):
        ax.text(value + 1.2, y, f"{value:.1f}", va="center", fontsize=9, color=MUTED)
    sns.despine(left=True, bottom=False)
    save(fig, "priority_hotspots.png")


def sector_heatmap(states: pd.DataFrame) -> None:
    columns = [
        "food_insecurity_pct",
        "wash_gap_pct",
        "health_gap_pct",
        "access_constraint",
        "funding_gap_pct",
    ]
    labels = ["Food", "WASH", "Health", "Access", "Funding"]
    heat = states.nlargest(10, "priority_score").set_index("state")[columns] * 100
    fig, ax = plt.subplots(figsize=(8.8, 5.4))
    sns.heatmap(
        heat,
        cmap=sns.blend_palette([TEAL, AMBER, CORAL], as_cmap=True),
        annot=True,
        fmt=".0f",
        linewidths=0.5,
        linecolor="#edf1ea",
        cbar_kws={"label": "Pressure or gap (%)"},
        ax=ax,
    )
    ax.set_xticklabels(labels, rotation=0)
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_title("Sector Pressure Matrix for Top Hotspots", loc="left", color=GREEN, weight="bold")
    save(fig, "sector_pressure_heatmap.png")


def monthly_trends(trends: pd.DataFrame) -> None:
    fig, ax1 = plt.subplots(figsize=(9.2, 5.2))
    ax1.plot(trends["month"], trends["total_idps"] / 1_000_000, color=GREEN, lw=3, marker="o")
    ax1.set_ylabel("Estimated IDPs (millions)", color=GREEN)
    ax1.tick_params(axis="y", labelcolor=GREEN)
    ax1.grid(axis="y", alpha=0.22)

    ax2 = ax1.twinx()
    ax2.bar(
        trends["month"],
        trends["feedback_messages"],
        width=18,
        alpha=0.28,
        color=ORANGE,
        label="Feedback records",
    )
    ax2.set_ylabel("Synthetic feedback records", color=ORANGE)
    ax2.tick_params(axis="y", labelcolor=ORANGE)

    ax1.set_title("Displacement and Feedback Signal Trend", loc="left", color=GREEN, weight="bold")
    ax1.set_xlabel("")
    fig.autofmt_xdate(rotation=30, ha="right")
    sns.despine(ax=ax1, right=False)
    save(fig, "monthly_trends.png")


def feedback_urgency(feedback: pd.DataFrame) -> None:
    urgency_order = ["Critical", "High", "Medium"]
    pivot = (
        feedback.pivot_table(index="sector", columns="urgency", values="message", aggfunc="count", fill_value=0)
        .reindex(columns=urgency_order, fill_value=0)
        .sort_values(urgency_order, ascending=False)
    )
    fig, ax = plt.subplots(figsize=(8.8, 5.2))
    bottom = np.zeros(len(pivot))
    colors = {"Critical": CORAL, "High": AMBER, "Medium": TEAL}
    for urgency in urgency_order:
        values = pivot[urgency].to_numpy()
        ax.bar(pivot.index, values, bottom=bottom, color=colors[urgency], label=urgency)
        bottom += values
    ax.set_ylabel("Synthetic feedback records")
    ax.set_xlabel("")
    ax.set_title("Feedback Signals by Sector and Urgency", loc="left", color=GREEN, weight="bold")
    ax.legend(frameon=False, ncols=3, loc="upper right")
    ax.tick_params(axis="x", rotation=25)
    ax.grid(axis="y", alpha=0.2)
    sns.despine()
    save(fig, "feedback_urgency.png")


def pipeline_diagram() -> None:
    fig, ax = plt.subplots(figsize=(9.4, 3.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis("off")
    steps = [
        ("Public context\nand synthetic data", 0.3, BLUE),
        ("Preprocessing\nand scoring", 2.35, TEAL),
        ("Local NLP\ntriage", 4.35, AMBER),
        ("Dashboard\nvisuals", 6.35, ORANGE),
        ("AI Action\nBrief", 8.25, CORAL),
    ]
    for label, x, color in steps:
        box = FancyBboxPatch(
            (x, 0.85),
            1.35,
            1.25,
            boxstyle="round,pad=0.08,rounding_size=0.08",
            linewidth=1.1,
            edgecolor=color,
            facecolor="#ffffff",
        )
        ax.add_patch(box)
        ax.text(x + 0.675, 1.48, label, ha="center", va="center", fontsize=9.5, weight="bold", color="#17211c")
    for i in range(len(steps) - 1):
        start = steps[i][1] + 1.35
        end = steps[i + 1][1]
        arrow = FancyArrowPatch(
            (start + 0.1, 1.48),
            (end - 0.1, 1.48),
            arrowstyle="-|>",
            mutation_scale=14,
            linewidth=1.4,
            color=MUTED,
        )
        ax.add_patch(arrow)
    ax.text(0.3, 2.55, "Technical Workflow", color=GREEN, fontsize=15, weight="bold")
    ax.text(
        0.3,
        0.25,
        "Design principle: transparent decision support with human validation, not automated humanitarian allocation.",
        color=MUTED,
        fontsize=9.5,
    )
    save(fig, "technical_pipeline.png")


def main() -> None:
    sns.set_theme(style="white", font="DejaVu Sans")
    states = score_states(pd.read_csv(DATA_DIR / "state_needs.csv"))
    trends = pd.read_csv(DATA_DIR / "monthly_trends.csv", parse_dates=["month"])
    feedback = pd.read_csv(DATA_DIR / "feedback_samples.csv", parse_dates=["date"])

    priority_bar(states)
    sector_heatmap(states)
    monthly_trends(trends)
    feedback_urgency(feedback)
    pipeline_diagram()


if __name__ == "__main__":
    main()
