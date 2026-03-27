

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Experiment Comparison Dashboard",
    page_icon="📊",
    layout="wide",
)

DATA_FILES = {
    "A": "experiment_A_standard_classical_simple.csv",
    "B": "experiment_B_complex_classical.csv",
    "C": "experiment_C_quantum_approach.csv",
}

APPROACH_LABELS = {
    "A": "Standard Classical",
    "B": "Complex Classical",
    "C": "Quantum Approach",
}

METRIC_LABELS = {
    "elapsed_seconds": "Elapsed Seconds",
    "current_objective_score": "Current Objective Score",
    "best_objective_score": "Best Objective Score",
    "best_improvement_pct": "Best Improvement %",
    "success_rate_pct": "Success Rate %",
    "stability_score_pct": "Stability Score %",
    "error_or_noise_pct": "Error / Noise %",
    "memory_mb": "Memory (MB)",
    "energy_cost_units": "Energy Cost Units",
}

HIGHER_IS_BETTER = {
    "current_objective_score": True,
    "best_objective_score": True,
    "best_improvement_pct": True,
    "success_rate_pct": True,
    "stability_score_pct": True,
    "elapsed_seconds": False,
    "error_or_noise_pct": False,
    "memory_mb": False,
    "energy_cost_units": False,
}

NUMERIC_COLUMNS = list(METRIC_LABELS.keys())
PERCENT_COLUMNS = {
    "best_improvement_pct",
    "success_rate_pct",
    "stability_score_pct",
    "error_or_noise_pct",
}


def resolve_path(filename: str) -> Path:
    candidates = [
        Path(__file__).resolve().parent / filename,
        Path("/mnt/data") / filename,
        Path.cwd() / filename,
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(f"Could not locate required data file: {filename}")


@st.cache_data
def load_data() -> pd.DataFrame:
    frames: List[pd.DataFrame] = []
    for code, filename in DATA_FILES.items():
        df = pd.read_csv(resolve_path(filename))
        df["approach_code"] = code
        df["approach_name"] = APPROACH_LABELS[code]
        frames.append(df)

    data = pd.concat(frames, ignore_index=True)
    data["run_label"] = data["approach_code"] + " • " + data["run_id"].astype(str)
    return data


def format_value(column: str, value: float) -> str:
    if pd.isna(value):
        return "—"
    if column in PERCENT_COLUMNS:
        return f"{value:,.2f}%"
    if column in {"elapsed_seconds", "current_objective_score", "best_objective_score", "memory_mb", "energy_cost_units"}:
        return f"{value:,.2f}"
    return f"{value:,.2f}"


@st.cache_data
def summarize(data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    final_per_run = (
        data.sort_values(["approach_code", "run_id", "iteration"])
        .groupby(["approach_code", "approach_name", "run_id"], as_index=False)
        .tail(1)
        .reset_index(drop=True)
    )

    approach_summary = (
        final_per_run.groupby(["approach_code", "approach_name"], as_index=False)[NUMERIC_COLUMNS]
        .mean()
        .sort_values("approach_code")
    )

    variability_summary = (
        final_per_run.groupby(["approach_code", "approach_name"], as_index=False)[NUMERIC_COLUMNS]
        .std()
        .fillna(0)
        .sort_values("approach_code")
    )

    return {
        "final_per_run": final_per_run,
        "approach_summary": approach_summary,
        "variability_summary": variability_summary,
    }


def winner_row(summary_df: pd.DataFrame, metric: str) -> pd.Series:
    ascending = not HIGHER_IS_BETTER.get(metric, True)
    return summary_df.sort_values(metric, ascending=ascending).iloc[0]


raw = load_data()
summary = summarize(raw)
final_per_run = summary["final_per_run"]
approach_summary = summary["approach_summary"]
variability_summary = summary["variability_summary"]

st.title("Experiment Comparison Dashboard")
st.caption("Single-file Streamlit dashboard comparing three optimization approaches across runs and iterations.")

with st.sidebar:
    st.header("Controls")
    selected_approaches = st.multiselect(
        "Approaches",
        options=approach_summary["approach_name"].tolist(),
        default=approach_summary["approach_name"].tolist(),
    )
    selected_metric = st.selectbox(
        "Primary comparison metric",
        options=NUMERIC_COLUMNS,
        format_func=lambda x: METRIC_LABELS[x],
        index=NUMERIC_COLUMNS.index("best_objective_score"),
    )
    selected_run_ids = st.multiselect(
        "Run IDs",
        options=sorted(raw["run_id"].unique().tolist()),
        default=sorted(raw["run_id"].unique().tolist()),
    )
    show_raw = st.checkbox("Show raw data table", value=False)

filtered_raw = raw[
    raw["approach_name"].isin(selected_approaches) & raw["run_id"].isin(selected_run_ids)
].copy()
filtered_final = final_per_run[
    final_per_run["approach_name"].isin(selected_approaches) & final_per_run["run_id"].isin(selected_run_ids)
].copy()
filtered_summary = approach_summary[approach_summary["approach_name"].isin(selected_approaches)].copy()
filtered_variability = variability_summary[variability_summary["approach_name"].isin(selected_approaches)].copy()

if filtered_raw.empty:
    st.warning("No data matches the current filters.")
    st.stop()

best_overall = winner_row(filtered_summary, selected_metric)
lowest_energy = winner_row(filtered_summary, "energy_cost_units")
lowest_memory = winner_row(filtered_summary, "memory_mb")
highest_success = winner_row(filtered_summary, "success_rate_pct")

c1, c2, c3, c4 = st.columns(4)
c1.metric(
    f"Best Avg {METRIC_LABELS[selected_metric]}",
    best_overall["approach_name"],
    format_value(selected_metric, best_overall[selected_metric]),
)
c2.metric(
    "Best Avg Success Rate",
    highest_success["approach_name"],
    format_value("success_rate_pct", highest_success["success_rate_pct"]),
)
c3.metric(
    "Lowest Avg Energy",
    lowest_energy["approach_name"],
    format_value("energy_cost_units", lowest_energy["energy_cost_units"]),
)
c4.metric(
    "Lowest Avg Memory",
    lowest_memory["approach_name"],
    format_value("memory_mb", lowest_memory["memory_mb"]),
)

left, right = st.columns([1.3, 1])

with left:
    st.subheader("Metric trend by iteration")
    trend_df = (
        filtered_raw.groupby(["approach_name", "iteration"], as_index=False)[selected_metric]
        .mean()
        .sort_values(["approach_name", "iteration"])
    )
    fig_trend = px.line(
        trend_df,
        x="iteration",
        y=selected_metric,
        color="approach_name",
        markers=True,
        labels={"iteration": "Iteration", selected_metric: METRIC_LABELS[selected_metric], "approach_name": "Approach"},
    )
    fig_trend.update_layout(legend_title_text="Approach", height=430)
    st.plotly_chart(fig_trend, use_container_width=True)

with right:
    st.subheader("Average final performance")
    bar_df = filtered_summary.sort_values(selected_metric, ascending=not HIGHER_IS_BETTER.get(selected_metric, True))
    fig_bar = px.bar(
        bar_df,
        x="approach_name",
        y=selected_metric,
        text=selected_metric,
        labels={"approach_name": "Approach", selected_metric: METRIC_LABELS[selected_metric]},
    )
    fig_bar.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig_bar.update_layout(showlegend=False, height=430)
    st.plotly_chart(fig_bar, use_container_width=True)

left2, right2 = st.columns([1, 1])

with left2:
    st.subheader("Final run distribution")
    fig_box = px.box(
        filtered_final,
        x="approach_name",
        y=selected_metric,
        points="all",
        labels={"approach_name": "Approach", selected_metric: METRIC_LABELS[selected_metric]},
    )
    fig_box.update_layout(showlegend=False, height=420)
    st.plotly_chart(fig_box, use_container_width=True)

with right2:
    st.subheader("Efficiency trade-off")
    scatter_df = filtered_final.copy()
    fig_scatter = px.scatter(
        scatter_df,
        x="energy_cost_units",
        y="best_objective_score",
        size="success_rate_pct",
        color="approach_name",
        hover_data=["run_id", "memory_mb", "stability_score_pct", "error_or_noise_pct"],
        labels={
            "energy_cost_units": "Energy Cost Units",
            "best_objective_score": "Best Objective Score",
            "success_rate_pct": "Success Rate %",
            "approach_name": "Approach",
        },
    )
    fig_scatter.update_layout(height=420)
    st.plotly_chart(fig_scatter, use_container_width=True)

st.subheader("Approach scorecard")
scorecard = filtered_summary[["approach_name"] + NUMERIC_COLUMNS].copy()
scorecard = scorecard.rename(columns=METRIC_LABELS)
st.dataframe(scorecard, use_container_width=True, hide_index=True)

st.subheader("Run-to-run variability (standard deviation of final run values)")
variability_display = filtered_variability[["approach_name"] + NUMERIC_COLUMNS].copy()
variability_display = variability_display.rename(columns=METRIC_LABELS)
st.dataframe(variability_display, use_container_width=True, hide_index=True)

st.subheader("Key takeaways")
winning_best = winner_row(filtered_summary, "best_objective_score")
winning_speed = winner_row(filtered_summary, "elapsed_seconds")
winning_stability = winner_row(filtered_summary, "stability_score_pct")
winning_noise = winner_row(filtered_summary, "error_or_noise_pct")

st.markdown(
    f"""
- **Best objective performance:** {winning_best['approach_name']} with an average final best objective score of **{format_value('best_objective_score', winning_best['best_objective_score'])}**.
- **Fastest execution:** {winning_speed['approach_name']} with average elapsed time of **{format_value('elapsed_seconds', winning_speed['elapsed_seconds'])}**.
- **Most stable:** {winning_stability['approach_name']} with average stability score of **{format_value('stability_score_pct', winning_stability['stability_score_pct'])}**.
- **Lowest noise/error:** {winning_noise['approach_name']} with average error/noise of **{format_value('error_or_noise_pct', winning_noise['error_or_noise_pct'])}**.
"""
)

if show_raw:
    st.subheader("Raw experimental data")
    st.dataframe(filtered_raw, use_container_width=True, hide_index=True)
