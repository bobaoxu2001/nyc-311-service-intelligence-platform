"""Generate portfolio dashboard preview PNGs from exported KPI CSVs.

These are static mockups for recruiter/interviewer review. They are not Power BI
exports and should be treated as a visual preview of the report design.
"""

from __future__ import annotations

from pathlib import Path
import textwrap

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "outputs" / "sample_dashboard_data"
MOCKUP_DIR = PROJECT_ROOT / "docs" / "dashboard_mockups"

COLORS = {
    "ink": "#17202A",
    "muted": "#607080",
    "grid": "#E7ECF0",
    "blue": "#2166AC",
    "cyan": "#31A6A4",
    "green": "#2E7D32",
    "orange": "#F28E2B",
    "red": "#C0392B",
    "purple": "#6C5CE7",
    "light": "#F6F8FA",
}


def read_csv(name: str) -> pd.DataFrame:
    path = DATA_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run `make all` or `python src/transform_311.py` first.")
    return pd.read_csv(path)


def fmt_int(value: float) -> str:
    return f"{int(round(value)):,}"


def fmt_pct(value: float) -> str:
    return f"{value:.1%}"


def fmt_hours(value: float) -> str:
    return f"{value:.1f}h"


def weighted_average(frame: pd.DataFrame, value_col: str, weight_col: str = "total_requests") -> float:
    valid = frame[[value_col, weight_col]].dropna()
    if valid.empty or valid[weight_col].sum() == 0:
        return 0.0
    return float(np.average(valid[value_col], weights=valid[weight_col]))


def add_title(fig: plt.Figure, title: str, subtitle: str) -> None:
    fig.text(0.04, 0.965, title, fontsize=22, fontweight="bold", color=COLORS["ink"])
    fig.text(0.04, 0.935, subtitle, fontsize=10.5, color=COLORS["muted"])


def style_axis(ax: plt.Axes) -> None:
    ax.set_facecolor("white")
    ax.grid(axis="x", color=COLORS["grid"], linewidth=0.8)
    ax.tick_params(colors=COLORS["muted"], labelsize=9)
    for spine in ax.spines.values():
        spine.set_visible(False)


def card(ax: plt.Axes, label: str, value: str, note: str, color: str) -> None:
    ax.axis("off")
    rect = FancyBboxPatch(
        (0, 0),
        1,
        1,
        boxstyle="round,pad=0.018,rounding_size=0.025",
        transform=ax.transAxes,
        facecolor="white",
        edgecolor=COLORS["grid"],
        linewidth=1.0,
    )
    ax.add_patch(rect)
    ax.text(0.06, 0.75, label.upper(), fontsize=9, color=COLORS["muted"], fontweight="bold", transform=ax.transAxes)
    ax.text(0.06, 0.40, value, fontsize=24, color=color, fontweight="bold", transform=ax.transAxes)
    ax.text(0.06, 0.16, note, fontsize=8.5, color=COLORS["muted"], transform=ax.transAxes, wrap=True)


def save(fig: plt.Figure, name: str) -> None:
    MOCKUP_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(MOCKUP_DIR / name, dpi=160, bbox_inches="tight", facecolor="#F3F6F8")
    plt.close(fig)


def load_data() -> dict[str, pd.DataFrame]:
    return {
        "agency": read_csv("agency_performance_kpis.csv"),
        "anomalies": read_csv("anomalies.csv"),
        "backlog": read_csv("backlog_kpis.csv"),
        "borough": read_csv("borough_service_kpis.csv"),
        "complaint": read_csv("complaint_type_kpis.csv"),
        "daily": read_csv("daily_request_kpis.csv"),
        "monthly": read_csv("monthly_request_kpis.csv"),
    }


def render_executive_overview(data: dict[str, pd.DataFrame]) -> None:
    borough = data["borough"]
    complaint = data["complaint"].sort_values("total_requests", ascending=False).head(8)
    daily = data["daily"].copy()
    daily["request_date"] = pd.to_datetime(daily["request_date"])
    daily_trend = daily.groupby("request_date", as_index=False)["total_requests"].sum()
    total = borough["total_requests"].sum()
    open_requests = borough["open_requests"].sum()
    backlog_rate = open_requests / total
    avg_resolution = weighted_average(borough, "avg_resolution_hours")
    pct_7d = weighted_average(borough, "pct_closed_within_7d")

    fig = plt.figure(figsize=(16, 10), facecolor="#F3F6F8")
    add_title(
        fig,
        "Executive Operations Overview",
        "NYC 311 demand, backlog exposure, and response performance | Static preview from CSV outputs",
    )
    gs = GridSpec(4, 4, figure=fig, left=0.04, right=0.98, top=0.89, bottom=0.06, hspace=0.55, wspace=0.35)

    card(fig.add_subplot(gs[0, 0]), "Total Requests", fmt_int(total), "Recent 100K public-data sample", COLORS["blue"])
    card(fig.add_subplot(gs[0, 1]), "Backlog Rate", fmt_pct(backlog_rate), f"{fmt_int(open_requests)} open requests", COLORS["red"])
    card(fig.add_subplot(gs[0, 2]), "Avg Resolution", fmt_hours(avg_resolution), "Weighted by borough volume", COLORS["orange"])
    card(fig.add_subplot(gs[0, 3]), "Closed in 7 Days", fmt_pct(pct_7d), "Operational SLA proxy", COLORS["green"])

    ax = fig.add_subplot(gs[1:3, :2])
    ax.plot(daily_trend["request_date"], daily_trend["total_requests"], color=COLORS["blue"], linewidth=2.6)
    ax.fill_between(daily_trend["request_date"], daily_trend["total_requests"], color=COLORS["blue"], alpha=0.12)
    ax.set_title("Daily Request Volume", loc="left", fontsize=13, fontweight="bold", color=COLORS["ink"])
    ax.set_ylabel("Requests", color=COLORS["muted"])
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    style_axis(ax)

    ax = fig.add_subplot(gs[1:3, 2:])
    labels = [textwrap.fill(x, 18) for x in complaint["complaint_type"]]
    ax.barh(labels[::-1], complaint["total_requests"][::-1], color=COLORS["cyan"])
    ax.set_title("Top Complaint Types", loc="left", fontsize=13, fontweight="bold", color=COLORS["ink"])
    ax.set_xlabel("Requests", color=COLORS["muted"])
    style_axis(ax)

    ax = fig.add_subplot(gs[3, :])
    b = borough.sort_values("total_requests", ascending=False)
    x = np.arange(len(b))
    ax.bar(x - 0.18, b["total_requests"], width=0.36, color=COLORS["blue"], label="Volume")
    ax2 = ax.twinx()
    ax2.plot(x + 0.18, b["backlog_rate"], color=COLORS["red"], marker="o", linewidth=2, label="Backlog rate")
    ax.set_xticks(x)
    ax.set_xticklabels(b["borough"], rotation=0)
    ax.set_title("Borough Demand vs. Backlog", loc="left", fontsize=13, fontweight="bold", color=COLORS["ink"])
    ax.set_ylabel("Requests", color=COLORS["muted"])
    ax2.set_ylabel("Backlog rate", color=COLORS["muted"])
    ax2.yaxis.set_major_formatter(lambda y, _: f"{y:.0%}")
    style_axis(ax)
    for spine in ax2.spines.values():
        spine.set_visible(False)
    save(fig, "executive_overview.png")


def render_agency_performance(data: dict[str, pd.DataFrame]) -> None:
    agency = data["agency"].copy()
    backlog = data["backlog"].copy()
    top_volume = agency.sort_values("total_requests", ascending=False).head(8)
    top_backlog = backlog[backlog["total_requests"] >= 50].sort_values("backlog_rate", ascending=False).head(8)
    high_risk_count = int(backlog["high_risk_backlog_flag"].sum())

    fig = plt.figure(figsize=(16, 10), facecolor="#F3F6F8")
    add_title(fig, "Agency Performance & Backlog Risk", "Volume, backlog exposure, and workflow review candidates by agency")
    gs = GridSpec(3, 3, figure=fig, left=0.04, right=0.98, top=0.89, bottom=0.06, hspace=0.52, wspace=0.42)

    card(fig.add_subplot(gs[0, 0]), "High-Risk Combos", fmt_int(high_risk_count), "Agency/borough rows flagged by backlog rule", COLORS["red"])
    card(fig.add_subplot(gs[0, 1]), "Largest Agency", top_volume.iloc[0]["agency"], f"{fmt_int(top_volume.iloc[0]['total_requests'])} requests", COLORS["blue"])
    slow = agency.sort_values("avg_resolution_hours", ascending=False).iloc[0]
    card(fig.add_subplot(gs[0, 2]), "Slowest Avg", slow["agency"], fmt_hours(slow["avg_resolution_hours"]), COLORS["orange"])

    ax = fig.add_subplot(gs[1:, 0])
    labels = [textwrap.fill(x, 14) for x in top_volume["agency"]]
    ax.barh(labels[::-1], top_volume["total_requests"][::-1], color=COLORS["blue"])
    ax.set_title("Agency Volume Ranking", loc="left", fontsize=13, fontweight="bold", color=COLORS["ink"])
    ax.set_xlabel("Requests", color=COLORS["muted"])
    style_axis(ax)

    ax = fig.add_subplot(gs[1:, 1])
    ax.scatter(
        agency["total_requests"],
        agency["backlog_rate"],
        s=np.clip(agency["avg_resolution_hours"].fillna(0), 5, 120) * 3,
        c=agency["avg_resolution_hours"].fillna(0),
        cmap="YlOrRd",
        alpha=0.75,
        edgecolor="white",
        linewidth=0.6,
    )
    label_candidates = agency[(agency["backlog_rate"] >= 0.10) | (agency["total_requests"] < agency["total_requests"].max() * 0.65)]
    for _, row in label_candidates.sort_values("total_requests", ascending=False).head(5).iterrows():
        ax.annotate(row["agency"], (row["total_requests"], row["backlog_rate"]), fontsize=8, color=COLORS["ink"])
    ax.set_title("Volume vs. Backlog Risk", loc="left", fontsize=13, fontweight="bold", color=COLORS["ink"])
    ax.set_xlabel("Requests", color=COLORS["muted"])
    ax.set_ylabel("Backlog rate", color=COLORS["muted"])
    ax.yaxis.set_major_formatter(lambda y, _: f"{y:.0%}")
    style_axis(ax)

    ax = fig.add_subplot(gs[1:, 2])
    labels = [f"{r.agency} / {r.borough}" for r in top_backlog.itertuples(index=False)]
    ax.barh([textwrap.fill(x, 18) for x in labels[::-1]], top_backlog["backlog_rate"][::-1], color=COLORS["red"])
    ax.set_title("Backlog Review Queue", loc="left", fontsize=13, fontweight="bold", color=COLORS["ink"])
    ax.set_xlabel("Backlog rate", color=COLORS["muted"])
    ax.xaxis.set_major_formatter(lambda y, _: f"{y:.0%}")
    style_axis(ax)
    save(fig, "agency_performance.png")


def render_borough_complaint(data: dict[str, pd.DataFrame]) -> None:
    borough = data["borough"].sort_values("total_requests", ascending=False)
    daily = data["daily"].copy()
    top_complaints = data["complaint"].sort_values("total_requests", ascending=False).head(8)["complaint_type"]
    matrix = (
        daily[daily["complaint_type"].isin(top_complaints)]
        .pivot_table(index="complaint_type", columns="borough", values="total_requests", aggfunc="sum", fill_value=0)
        .reindex(top_complaints)
    )

    fig = plt.figure(figsize=(16, 10), facecolor="#F3F6F8")
    add_title(
        fig,
        "Borough / Complaint Demand Intelligence",
        "Demand mix by borough and complaint type, with map-ready fields available in the star schema",
    )
    gs = GridSpec(2, 3, figure=fig, left=0.04, right=0.98, top=0.88, bottom=0.08, hspace=0.45, wspace=0.42)

    ax = fig.add_subplot(gs[:, 0])
    ax.barh(borough["borough"][::-1], borough["total_requests"][::-1], color=COLORS["blue"])
    ax.set_title("Borough Request Volume", loc="left", fontsize=13, fontweight="bold", color=COLORS["ink"])
    ax.set_xlabel("Requests", color=COLORS["muted"])
    style_axis(ax)

    ax = fig.add_subplot(gs[0, 1:])
    im = ax.imshow(matrix.values, aspect="auto", cmap="Blues")
    ax.set_yticks(range(len(matrix.index)))
    ax.set_yticklabels([textwrap.fill(x, 22) for x in matrix.index], fontsize=8)
    ax.set_xticks(range(len(matrix.columns)))
    ax.set_xticklabels(matrix.columns, fontsize=8)
    ax.set_title("Complaint Mix Heatmap", loc="left", fontsize=13, fontweight="bold", color=COLORS["ink"])
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02)

    ax = fig.add_subplot(gs[1, 1:])
    mix = matrix.div(matrix.sum(axis=0), axis=1).fillna(0)
    bottom = np.zeros(len(mix.columns))
    palette = [COLORS["blue"], COLORS["cyan"], COLORS["orange"], COLORS["green"], COLORS["purple"], "#7F8C8D", "#B56576", "#6D597A"]
    for idx, complaint in enumerate(mix.index):
        ax.bar(mix.columns, mix.loc[complaint], bottom=bottom, label=textwrap.shorten(complaint, 22), color=palette[idx % len(palette)])
        bottom += mix.loc[complaint].values
    ax.set_title("Top Complaint Share by Borough", loc="left", fontsize=13, fontweight="bold", color=COLORS["ink"])
    ax.set_ylabel("Share of top complaint volume", color=COLORS["muted"])
    ax.yaxis.set_major_formatter(lambda y, _: f"{y:.0%}")
    ax.legend(ncol=2, fontsize=7, loc="upper right", frameon=False)
    style_axis(ax)
    save(fig, "borough_complaint_analysis.png")


def render_ai_risk_monitor(data: dict[str, pd.DataFrame]) -> None:
    anomalies = data["anomalies"].copy()
    backlog = data["backlog"].copy()
    anomalies["request_date"] = pd.to_datetime(anomalies["request_date"]).dt.date
    top_anomalies = anomalies.sort_values(["request_date", "z_score"], ascending=[False, False]).head(8)
    high_risk = backlog[backlog["high_risk_backlog_flag"]].sort_values(["backlog_rate", "total_requests"], ascending=[False, False]).head(8)

    fig = plt.figure(figsize=(16, 10), facecolor="#F3F6F8")
    add_title(fig, "AI Risk & Anomaly Monitor", "Explainable spike detection using rolling baselines, z-scores, and IQR checks")
    gs = GridSpec(3, 4, figure=fig, left=0.04, right=0.98, top=0.88, bottom=0.06, hspace=0.55, wspace=0.38)

    card(fig.add_subplot(gs[0, 0]), "Anomalies", fmt_int(len(anomalies)), "Daily borough/complaint spikes", COLORS["red"])
    top = top_anomalies.iloc[0]
    card(fig.add_subplot(gs[0, 1]), "Latest Spike", top["borough"], f"{top['complaint_type']} | {fmt_int(top['total_requests'])} requests", COLORS["orange"])
    card(fig.add_subplot(gs[0, 2]), "Max Z-Score", f"{anomalies['z_score'].max():.1f}", "Largest statistical deviation", COLORS["purple"])
    card(fig.add_subplot(gs[0, 3]), "Backlog Flags", fmt_int(backlog["high_risk_backlog_flag"].sum()), "Agency/borough combos", COLORS["red"])

    ax = fig.add_subplot(gs[1:, :2])
    labels = [f"{r.borough}: {textwrap.shorten(r.complaint_type, 24)}" for r in top_anomalies.itertuples(index=False)]
    ax.barh(labels[::-1], top_anomalies["z_score"][::-1], color=COLORS["red"])
    ax.axvline(3, color=COLORS["muted"], linestyle="--", linewidth=1)
    ax.set_title("Top Recent Anomaly Scores", loc="left", fontsize=13, fontweight="bold", color=COLORS["ink"])
    ax.set_xlabel("Z-score", color=COLORS["muted"])
    style_axis(ax)

    ax = fig.add_subplot(gs[1:, 2:])
    ax.axis("off")
    ax.set_title("Operational Action Queue", loc="left", fontsize=13, fontweight="bold", color=COLORS["ink"])
    rows = []
    for r in high_risk.head(6).itertuples(index=False):
        rows.append([f"{r.agency} / {r.borough}", fmt_int(r.total_requests), fmt_pct(r.backlog_rate)])
    table = ax.table(
        cellText=rows,
        colLabels=["Agency / Borough", "Volume", "Backlog"],
        loc="upper left",
        colLoc="left",
        cellLoc="left",
        bbox=[0.0, 0.18, 1.0, 0.72],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    for (row, _), cell in table.get_celld().items():
        cell.set_edgecolor(COLORS["grid"])
        if row == 0:
            cell.set_text_props(weight="bold", color=COLORS["ink"])
            cell.set_facecolor("#EAF1F8")
        else:
            cell.set_facecolor("white")
    ax.text(
        0,
        0.05,
        "Recommended cadence: weekly anomaly review, agency queue triage, and data-quality exception validation before executive reporting.",
        fontsize=10,
        color=COLORS["muted"],
        wrap=True,
        transform=ax.transAxes,
    )
    save(fig, "ai_risk_anomaly_monitor.png")


def render_fabric_architecture_blueprint() -> None:
    fig = plt.figure(figsize=(16, 8.5), facecolor="#F3F6F8")
    ax = fig.add_subplot(111)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    fig.text(
        0.04,
        0.94,
        "Microsoft Fabric-Ready Reference Architecture",
        fontsize=22,
        fontweight="bold",
        color=COLORS["ink"],
    )
    fig.text(
        0.04,
        0.90,
        "Local Python/DuckDB prototype mapped to Fabric components; not a deployed Fabric workspace",
        fontsize=10.5,
        color=COLORS["muted"],
    )

    nodes = [
        ("NYC Open Data API\n311 Service Requests", 0.06, 0.66, COLORS["blue"]),
        ("Data Factory /\nDataflow Gen2\norchestration", 0.22, 0.66, COLORS["cyan"]),
        ("OneLake Raw /\nBronze zone\nparquet + metadata", 0.38, 0.66, COLORS["blue"]),
        ("Fabric Lakehouse\nSilver layer\nclean + quality flags", 0.54, 0.66, COLORS["green"]),
        ("Fabric Warehouse\nGold marts\nstar schema + KPIs", 0.70, 0.66, COLORS["orange"]),
        ("Power BI\nSemantic model\nDAX + relationships", 0.86, 0.66, COLORS["purple"]),
    ]

    for text, x, y, color in nodes:
        box = FancyBboxPatch(
            (x - 0.065, y - 0.085),
            0.13,
            0.17,
            boxstyle="round,pad=0.018,rounding_size=0.02",
            transform=ax.transAxes,
            facecolor="white",
            edgecolor=color,
            linewidth=2,
        )
        ax.add_patch(box)
        ax.text(x, y, text, ha="center", va="center", fontsize=9.5, color=COLORS["ink"], fontweight="bold", transform=ax.transAxes)

    for i in range(len(nodes) - 1):
        x1 = nodes[i][1] + 0.07
        x2 = nodes[i + 1][1] - 0.07
        y = nodes[i][2]
        arrow = FancyArrowPatch(
            (x1, y),
            (x2, y),
            arrowstyle="-|>",
            mutation_scale=14,
            linewidth=1.8,
            color=COLORS["muted"],
            transform=ax.transAxes,
        )
        ax.add_patch(arrow)

    lower_nodes = [
        ("Executive dashboards\noperations, agency, borough", 0.78, 0.34, COLORS["blue"]),
        ("AI Risk Monitor\nexplainable anomaly detection", 0.54, 0.34, COLORS["red"]),
        ("Governance / QA layer\nmetric certification, access,\nmonitoring, responsible AI", 0.30, 0.34, COLORS["green"]),
    ]
    for text, x, y, color in lower_nodes:
        box = FancyBboxPatch(
            (x - 0.10, y - 0.075),
            0.20,
            0.15,
            boxstyle="round,pad=0.018,rounding_size=0.02",
            transform=ax.transAxes,
            facecolor="white",
            edgecolor=color,
            linewidth=2,
        )
        ax.add_patch(box)
        ax.text(x, y, text, ha="center", va="center", fontsize=9.5, color=COLORS["ink"], fontweight="bold", transform=ax.transAxes)

    for start, end in [((0.86, 0.57), (0.78, 0.42)), ((0.70, 0.57), (0.54, 0.42)), ((0.54, 0.57), (0.30, 0.42)), ((0.30, 0.42), (0.54, 0.57)), ((0.30, 0.42), (0.86, 0.57))]:
        ax.add_patch(
            FancyArrowPatch(
                start,
                end,
                arrowstyle="-|>",
                mutation_scale=12,
                linewidth=1.4,
                color=COLORS["muted"],
                alpha=0.8,
                transform=ax.transAxes,
            )
        )

    ax.text(
        0.04,
        0.06,
        "Controls: source metadata, quality checks, certified metrics, role-based access, refresh monitoring, exception review, and human-in-the-loop anomaly validation.",
        fontsize=10,
        color=COLORS["muted"],
        transform=ax.transAxes,
    )
    save(fig, "fabric_architecture_blueprint.png")


def main() -> None:
    data = load_data()
    render_executive_overview(data)
    render_agency_performance(data)
    render_borough_complaint(data)
    render_ai_risk_monitor(data)
    render_fabric_architecture_blueprint()
    print(f"Saved dashboard mockups to {MOCKUP_DIR}")


if __name__ == "__main__":
    main()
