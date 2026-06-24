#!/usr/bin/env python
"""Run UDA-city present/future SUEWS contrasts and create docs plots."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
import yaml
from supy.suews_sim import SUEWSSimulation


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "uda-city-hackathon"
DOCS = ROOT / "docs"
CONFIG = DATA / "uda-city.yml"
FUTURE_FORCING = DATA / "forcing" / "future_hot_humid" / "UDA_2024_data_60.txt"
SPINUP_DAYS = 14
ANALYSIS_DAYS = 30
HEAT_THRESHOLD_C = 35.0
SCENARIO_LABELS = {
    "present": "Present",
    "future_plus_2p5c": "+2.5 C future",
}
SEASON_ORDER = ["Winter", "Spring", "Summer", "Autumn"]
SEASON_BY_MONTH = {
    12: "Winter",
    1: "Winter",
    2: "Winter",
    3: "Spring",
    4: "Spring",
    5: "Spring",
    6: "Summer",
    7: "Summer",
    8: "Summer",
    9: "Autumn",
    10: "Autumn",
    11: "Autumn",
}


def minmax(series: pd.Series) -> pd.Series:
    lo = series.min()
    hi = series.max()
    if hi <= lo:
        return pd.Series(0.0, index=series.index)
    return (series - lo) / (hi - lo)


def load_neighbourhoods() -> pd.DataFrame:
    raw = yaml.safe_load((DATA / "neighbourhoods.yml").read_text(encoding="utf-8"))
    rows = []
    for item in raw["neighbourhoods"]:
        lc = item["land_cover_fractions"]
        rows.append(
            {
                "gridiv": int(item["gridiv"]),
                "name": item["name"],
                "type": item["type"],
                "paved": float(lc["paved"]),
                "bldgs": float(lc["bldgs"]),
                "evetr": float(lc["evetr"]),
                "dectr": float(lc["dectr"]),
                "grass": float(lc["grass"]),
                "bsoil": float(lc["bsoil"]),
                "water": float(lc["water"]),
                "population_day": float(item["population_density_per_ha"]["day"]),
                "population_night": float(item["population_density_per_ha"]["night"]),
            }
        )
    df = pd.DataFrame(rows)
    df["green_fraction"] = df["evetr"] + df["dectr"] + df["grass"]
    df["green_blue_fraction"] = df["green_fraction"] + df["water"]
    df["impervious_fraction"] = df["paved"] + df["bldgs"]
    return df


def select_contrast_zones(neighbourhoods: pd.DataFrame) -> dict[str, int]:
    core = neighbourhoods[neighbourhoods["type"].eq("core")]
    built = core.sort_values(["bldgs", "impervious_fraction"], ascending=False).iloc[0]
    refuge = neighbourhoods[neighbourhoods["type"].eq("refuge")]
    vegetated = refuge.sort_values(
        ["green_blue_fraction", "bldgs"], ascending=[False, True]
    ).iloc[0]
    return {
        "most_built_core": int(built["gridiv"]),
        "most_vegetated_suburban": int(vegetated["gridiv"]),
    }


def run_scenario(label: str, forcing: Path | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    sim = SUEWSSimulation(str(CONFIG))
    if forcing is not None:
        sim.update_forcing(str(forcing))
    # The full 91-day package is ideal for final runs, but it can exceed the
    # memory available in the desktop sandbox when SuPy expands every output
    # variable for all 10 grids. Keep the end-to-end check scientifically useful
    # by retaining the same scenarios and all sites, with 14 spin-up days plus
    # 30 analysis days.
    n_steps = (SPINUP_DAYS + ANALYSIS_DAYS) * 24 * 12
    forcing_df = sim.forcing.df.head(n_steps).copy()
    sim.update_forcing(forcing_df)
    sim.run()
    if not sim.is_complete:
        raise RuntimeError(f"{label} simulation did not complete")
    return sim.results.copy(), forcing_df


def hourly_from_results(label: str, results: pd.DataFrame) -> pd.DataFrame:
    needed = ["QH", "QE", "QN", "QS", "T2"]
    frames = []
    for grid in sorted(results.index.get_level_values(0).unique()):
        suews = results.loc[grid]["SUEWS"]
        missing = [col for col in needed if col not in suews.columns]
        if missing:
            raise KeyError(f"grid {grid} missing SUEWS columns: {missing}")
        hourly = suews[needed].resample("h").mean()
        hourly["gridiv"] = int(grid)
        hourly["scenario"] = label
        hourly = hourly.reset_index().rename(columns={hourly.index.name or "index": "time"})
        if "time" not in hourly.columns:
            hourly = hourly.rename(columns={hourly.columns[0]: "time"})
        frames.append(hourly)
    out = pd.concat(frames, ignore_index=True)
    out["time"] = pd.to_datetime(out["time"])
    return out[["scenario", "gridiv", "time", "QH", "QE", "QN", "QS", "T2"]]


def forcing_summary(label: str, forcing_df: pd.DataFrame) -> dict[str, float | str]:
    summary: dict[str, float | str] = {"scenario": label, "n_steps": float(len(forcing_df))}
    for col in ("Tair", "RH", "U", "pres", "kdown", "ldown", "rain"):
        if col in forcing_df.columns:
            series = forcing_df[col].astype(float)
            summary[f"{col}_mean"] = float(series.mean())
            summary[f"{col}_min"] = float(series.min())
            summary[f"{col}_max"] = float(series.max())
    return summary


def vulnerability_components(socio: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "elderly": socio["frac_over65"],
            "young": socio["frac_under5"],
            "no_ac": 1.0 - socio["ac_access"],
            "outdoor_work": socio["frac_outdoor_workers"],
            "deprivation": socio["deprivation_index"],
        },
        index=socio.index,
    )


def vulnerability_index(socio: pd.DataFrame) -> pd.Series:
    components = vulnerability_components(socio)
    return minmax(components.mean(axis=1))


def risk_level(score: float) -> str:
    if score >= 0.75:
        return "Critical"
    if score >= 0.50:
        return "High"
    if score >= 0.25:
        return "Moderate"
    return "Low"


def risk_table(hourly: pd.DataFrame, neighbourhoods: pd.DataFrame) -> pd.DataFrame:
    present = hourly[hourly["scenario"].eq("present") & hourly["after_spinup"]]
    hazard = (
        present.groupby("gridiv")["T2"]
        .apply(lambda s: int((s > HEAT_THRESHOLD_C).sum()))
        .rename("dangerous_heat_hours")
    )
    socio = pd.read_csv(DATA / "socioeconomic.csv").set_index("gridiv")
    df = neighbourhoods.set_index("gridiv").join(hazard)
    df["hazard"] = minmax(df["dangerous_heat_hours"].astype(float))
    df["exposure"] = minmax(df["population_day"].astype(float))
    df["vulnerability"] = vulnerability_index(socio)
    pillars = df[["hazard", "exposure", "vulnerability"]].clip(lower=0)
    df["risk_index_raw"] = pillars.prod(axis=1) ** (1.0 / 3.0)
    df["risk_index"] = minmax(df["risk_index_raw"])
    df["risk_rank"] = df["risk_index"].rank(ascending=False, method="min").astype(int)
    cols = [
        "name",
        "type",
        "dangerous_heat_hours",
        "population_day",
        "hazard",
        "exposure",
        "vulnerability",
        "risk_index",
        "risk_rank",
    ]
    return df.reset_index()[["gridiv"] + cols].sort_values("risk_rank")


def heat_risk_matrix(hourly: pd.DataFrame, neighbourhoods: pd.DataFrame) -> pd.DataFrame:
    socio = pd.read_csv(DATA / "socioeconomic.csv").set_index("gridiv")
    components = vulnerability_components(socio).add_prefix("vuln_")
    base = neighbourhoods.set_index("gridiv")[
        [
            "name",
            "type",
            "population_day",
            "population_night",
            "bldgs",
            "green_blue_fraction",
            "impervious_fraction",
        ]
    ].join(components)
    base["exposure"] = minmax(base["population_day"].astype(float))
    base["vulnerability"] = vulnerability_index(socio)

    rows = []
    for scenario in SCENARIO_LABELS:
        scenario_hourly = hourly[hourly["scenario"].eq(scenario) & hourly["after_spinup"]]
        hazard = (
            scenario_hourly.groupby("gridiv")["T2"]
            .agg(
                dangerous_heat_hours=lambda s: int((s > HEAT_THRESHOLD_C).sum()),
                analysis_hours="size",
                max_t2="max",
                mean_t2="mean",
            )
            .astype({"dangerous_heat_hours": int, "analysis_hours": int})
        )
        df = base.join(hazard)
        df["hazard"] = minmax(df["dangerous_heat_hours"].astype(float))
        pillars = df[["hazard", "exposure", "vulnerability"]].clip(lower=0)
        df["risk_index_raw"] = pillars.prod(axis=1) ** (1.0 / 3.0)
        df["risk_index"] = minmax(df["risk_index_raw"])
        df["risk_rank"] = df["risk_index"].rank(ascending=False, method="min").astype(int)
        df["risk_level"] = df["risk_index"].map(risk_level)
        df["scenario"] = scenario
        df["scenario_label"] = SCENARIO_LABELS[scenario]
        rows.append(df.reset_index())

    cols = [
        "scenario",
        "scenario_label",
        "gridiv",
        "name",
        "type",
        "dangerous_heat_hours",
        "analysis_hours",
        "max_t2",
        "mean_t2",
        "population_day",
        "hazard",
        "exposure",
        "vulnerability",
        "risk_index",
        "risk_level",
        "risk_rank",
        "vuln_elderly",
        "vuln_young",
        "vuln_no_ac",
        "vuln_outdoor_work",
        "vuln_deprivation",
        "bldgs",
        "green_blue_fraction",
        "impervious_fraction",
    ]
    matrix = pd.concat(rows, ignore_index=True)[cols]
    scenario_order = {scenario: idx for idx, scenario in enumerate(SCENARIO_LABELS)}
    matrix["_scenario_order"] = matrix["scenario"].map(scenario_order)
    matrix = matrix.sort_values(["_scenario_order", "risk_rank", "gridiv"]).drop(
        columns="_scenario_order"
    )
    matrix.to_csv(DOCS / "heat_risk_matrix.csv", index=False)
    critical = matrix[matrix["risk_level"].eq("Critical")].copy()
    critical.to_csv(DOCS / "critical_heat_risk_zones.csv", index=False)
    return matrix


def plot_heat_risk_matrix(matrix: pd.DataFrame) -> Path:
    colors = {
        "Critical": "#b2182b",
        "High": "#ef8a62",
        "Moderate": "#fdb863",
        "Low": "#4393c3",
    }
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharex=True, sharey=True)
    for ax, scenario in zip(axes, SCENARIO_LABELS):
        scenario_matrix = matrix[matrix["scenario"].eq(scenario)].copy()
        sizes = 90 + scenario_matrix["exposure"].to_numpy(dtype=float) * 560
        ax.scatter(
            scenario_matrix["hazard"],
            scenario_matrix["vulnerability"],
            s=sizes,
            c=scenario_matrix["risk_level"].map(colors),
            edgecolor="#333333",
            linewidth=0.8,
            alpha=0.92,
        )
        for row in scenario_matrix.itertuples(index=False):
            if row.risk_level in {"Critical", "High"}:
                ax.annotate(
                    row.name,
                    (row.hazard, row.vulnerability),
                    xytext=(5, 5),
                    textcoords="offset points",
                    fontsize=8.5,
                    color="#222222",
                )
        ax.axvline(0.5, color="#999999", linewidth=0.9, linestyle="--", alpha=0.7)
        ax.axhline(0.5, color="#999999", linewidth=0.9, linestyle="--", alpha=0.7)
        ax.set_title(SCENARIO_LABELS[scenario], loc="left", fontsize=13, weight="bold")
        ax.set_xlim(-0.04, 1.04)
        ax.set_ylim(-0.04, 1.04)
        ax.grid(True, color="#e0e0e0", linewidth=0.8, alpha=0.8)
        ax.spines[["top", "right"]].set_visible(False)

    axes[0].set_ylabel("Vulnerability score (0-1)")
    for ax in axes:
        ax.set_xlabel(f"Hazard score: hours with T2 > {HEAT_THRESHOLD_C:.0f} C (0-1)")

    level_handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            markerfacecolor=colors[level],
            markeredgecolor="#333333",
            markersize=9,
            label=level,
        )
        for level in ["Critical", "High", "Moderate", "Low"]
    ]
    size_handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            markerfacecolor="#ffffff",
            markeredgecolor="#333333",
            markersize=size,
            label=label,
        )
        for size, label in [(6, "lower exposure"), (12, "higher exposure")]
    ]
    fig.suptitle(
        "Socio-economic heat-risk matrix",
        x=0.06,
        ha="left",
        fontsize=16,
        weight="bold",
    )
    fig.legend(
        handles=[*level_handles, *size_handles],
        loc="upper center",
        bbox_to_anchor=(0.56, 0.96),
        ncols=6,
        frameon=False,
    )
    fig.subplots_adjust(top=0.82, left=0.08, right=0.98, bottom=0.12, wspace=0.15)

    png = DOCS / "heat_risk_matrix.png"
    svg = DOCS / "heat_risk_matrix.svg"
    fig.savefig(png, dpi=220, bbox_inches="tight")
    fig.savefig(svg, bbox_inches="tight")
    plt.close(fig)
    return png


def plot_diurnal(hourly: pd.DataFrame, risk: pd.DataFrame) -> Path:
    high_risk = risk.sort_values("risk_rank").iloc[0]
    grid = int(high_risk["gridiv"])
    zone_name = str(high_risk["name"])
    subset = hourly[hourly["gridiv"].eq(grid) & hourly["after_spinup"]].copy()

    # Compute future-present changes point by point first, then summarise those
    # deltas by local hour. This preserves the paired scenario signal instead
    # of subtracting already-smoothed curves.
    flux_cols = ["QN", "QH", "QE", "QS"]
    present = (
        subset[subset["scenario"].eq("present")]
        .set_index("time")[["hour"] + flux_cols]
        .sort_index()
    )
    future = (
        subset[subset["scenario"].eq("future_plus_2p5c")]
        .set_index("time")[flux_cols]
        .sort_index()
    )
    common_times = present.index.intersection(future.index)
    delta = future.loc[common_times, flux_cols] - present.loc[common_times, flux_cols]
    delta["hour"] = present.loc[common_times, "hour"]
    delta_out = delta.reset_index().rename(columns={"index": "time"})
    delta_out.insert(0, "name", zone_name)
    delta_out.insert(0, "gridiv", grid)
    delta_out.to_csv(DOCS / "hourly_deltas_high_risk_zone.csv", index=False)
    diurnal = delta.groupby("hour")[flux_cols].mean().reset_index()
    diurnal.to_csv(DOCS / "diurnal_deltas_high_risk_zone.csv", index=False)
    t2_diurnal = subset.groupby(["scenario", "hour"], as_index=False)["T2"].mean()

    flux_colors = {
        "QN": "#252525",
        "QH": "#d73027",
        "QE": "#1a9850",
        "QS": "#fdae61",
    }
    flux_labels = {
        "QN": "Delta QN net radiation",
        "QH": "Delta QH sensible",
        "QE": "Delta QE latent",
        "QS": "Delta QS storage",
    }

    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True, constrained_layout=True)
    for col in ["QN", "QS", "QE", "QH"]:
        axes[0].plot(
            diurnal["hour"],
            diurnal[col],
            label=flux_labels[col],
            color=flux_colors[col],
            linewidth=2.6,
        )
    t2_labels = {
        "present": "Present T2",
        "future_plus_2p5c": "+2.5 C scenario T2",
    }
    t2_colors = {
        "present": "#225ea8",
        "future_plus_2p5c": "#c51b7d",
    }
    for scenario in ["present", "future_plus_2p5c"]:
        group = t2_diurnal[t2_diurnal["scenario"].eq(scenario)]
        if group.empty:
            continue
        axes[1].plot(
            group["hour"],
            group["T2"],
            label=t2_labels[scenario],
            color=t2_colors[scenario],
            linewidth=2.8,
        )

    axes[0].set_title(
        f"Future-minus-present flux response with absolute T2: {zone_name} (gridiv {grid})",
        loc="left",
        fontsize=14,
        weight="bold",
    )
    axes[0].set_ylabel("Flux change (W m$^{-2}$)")
    axes[1].set_ylabel("T2 air temperature (deg C)")
    axes[1].set_xlabel("Local hour")
    axes[1].set_xticks(range(0, 24, 2))
    axes[0].axhline(0, color="#777777", linewidth=1.0, alpha=0.7)
    for ax in axes:
        ax.grid(True, color="#d9d9d9", linewidth=0.8, alpha=0.8)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].legend(frameon=False, ncols=2)
    axes[1].legend(frameon=False)

    png = DOCS / "diurnal_high_risk_zone.png"
    svg = DOCS / "diurnal_high_risk_zone.svg"
    fig.savefig(png, dpi=220, bbox_inches="tight")
    fig.savefig(svg, bbox_inches="tight")
    plt.close(fig)
    return png


def plot_seasonal_diurnal(hourly: pd.DataFrame, risk: pd.DataFrame) -> Path:
    high_risk = risk.sort_values("risk_rank").iloc[0]
    grid = int(high_risk["gridiv"])
    zone_name = str(high_risk["name"])
    subset = hourly[hourly["gridiv"].eq(grid) & hourly["after_spinup"]].copy()
    subset["season"] = subset["time"].dt.month.map(SEASON_BY_MONTH)

    flux_cols = ["QN", "QH", "QE", "QS"]
    present = (
        subset[subset["scenario"].eq("present")]
        .set_index("time")[["hour", "season"] + flux_cols]
        .sort_index()
    )
    future = (
        subset[subset["scenario"].eq("future_plus_2p5c")]
        .set_index("time")[flux_cols]
        .sort_index()
    )
    common_times = present.index.intersection(future.index)
    delta = future.loc[common_times, flux_cols] - present.loc[common_times, flux_cols]
    delta["hour"] = present.loc[common_times, "hour"]
    delta["season"] = present.loc[common_times, "season"]
    delta_out = delta.reset_index().rename(columns={"index": "time"})
    delta_out.insert(0, "name", zone_name)
    delta_out.insert(0, "gridiv", grid)
    delta_out.to_csv(DOCS / "seasonal_hourly_deltas_high_risk_zone.csv", index=False)

    diurnal = (
        delta.groupby(["season", "hour"], as_index=False)
        .agg(
            QN=("QN", "mean"),
            QH=("QH", "mean"),
            QE=("QE", "mean"),
            QS=("QS", "mean"),
            n_paired_hours=("QN", "size"),
        )
    )
    diurnal.to_csv(DOCS / "seasonal_diurnal_flux_deltas_high_risk_zone.csv", index=False)
    t2_diurnal = (
        subset.groupby(["season", "scenario", "hour"], as_index=False)
        .agg(T2=("T2", "mean"), n_hours=("T2", "size"))
    )
    t2_diurnal.to_csv(DOCS / "seasonal_diurnal_t2_high_risk_zone.csv", index=False)

    observed_coverage = (
        subset.groupby(["season", "scenario"], as_index=False)
        .agg(first_time=("time", "min"), last_time=("time", "max"), n_hours=("T2", "size"))
    )
    season_index = pd.MultiIndex.from_product(
        [SEASON_ORDER, ["present", "future_plus_2p5c"]],
        names=["season", "scenario"],
    ).to_frame(index=False)
    coverage = season_index.merge(observed_coverage, on=["season", "scenario"], how="left")
    coverage["n_hours"] = coverage["n_hours"].fillna(0).astype(int)
    coverage.to_csv(DOCS / "seasonal_data_coverage_high_risk_zone.csv", index=False)

    flux_colors = {
        "QN": "#252525",
        "QH": "#d73027",
        "QE": "#1a9850",
        "QS": "#fdae61",
    }
    flux_labels = {
        "QN": "Delta QN",
        "QH": "Delta QH",
        "QE": "Delta QE",
        "QS": "Delta QS",
    }
    t2_colors = {
        "present": "#225ea8",
        "future_plus_2p5c": "#c51b7d",
    }
    t2_labels = {
        "present": "Present T2",
        "future_plus_2p5c": "+2.5 C T2",
    }

    spring_delta = diurnal[diurnal["season"].eq("Spring")]
    spring_t2 = t2_diurnal[t2_diurnal["season"].eq("Spring")]
    spring_coverage = coverage[
        coverage["season"].eq("Spring") & coverage["scenario"].eq("present")
    ].iloc[0]

    fig, ax = plt.subplots(figsize=(11, 7))
    ax2 = ax.twinx()
    ax.set_title(
        "One-month spring-sample diurnal response",
        loc="left",
        fontsize=14,
        weight="bold",
    )
    ax.set_xlim(0, 23)
    ax.set_xticks(range(0, 24, 2))
    ax.set_xlabel("Local hour")
    ax.set_ylabel("Flux change (W m$^{-2}$)")
    ax2.set_ylabel("T2 air temperature (deg C)")
    ax.grid(True, color="#d9d9d9", linewidth=0.8, alpha=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    ax2.spines["top"].set_visible(False)

    if spring_delta.empty or spring_t2.empty:
        ax.text(
            0.5,
            0.5,
            "No Spring data in current run",
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=12,
            color="#666666",
        )
    else:
        for col in ["QN", "QS", "QE", "QH"]:
            ax.plot(
                spring_delta["hour"],
                spring_delta[col],
                color=flux_colors[col],
                linewidth=2.5,
            )
        for scenario in ["present", "future_plus_2p5c"]:
            group = spring_t2[spring_t2["scenario"].eq(scenario)]
            ax2.plot(
                group["hour"],
                group["T2"],
                color=t2_colors[scenario],
                linewidth=2.6,
                linestyle="--",
            )
        ax.axhline(0, color="#777777", linewidth=1.0, alpha=0.7)
        ax2.axhline(
            HEAT_THRESHOLD_C,
            color="#7f0000",
            linewidth=1.8,
            linestyle=":",
            alpha=0.9,
        )
        ax.text(
            0.02,
            0.96,
            (
                "Spring-month sample only\n"
                f"{spring_coverage['first_time']} to {spring_coverage['last_time']}\n"
                f"{spring_coverage['n_hours']} hourly values after spin-up"
            ),
            transform=ax.transAxes,
            ha="left",
            va="top",
            fontsize=10,
            color="#444444",
            bbox={"facecolor": "white", "edgecolor": "#dddddd", "alpha": 0.86, "pad": 6},
        )

    handles = [
        *[
            Line2D([0], [0], color=flux_colors[col], linewidth=2.4, label=flux_labels[col])
            for col in ["QN", "QS", "QE", "QH"]
        ],
        *[
            Line2D(
                [0],
                [0],
                color=t2_colors[scenario],
                linewidth=2.4,
                linestyle="--",
                label=t2_labels[scenario],
            )
            for scenario in ["present", "future_plus_2p5c"]
        ],
        Line2D(
            [0],
            [0],
            color="#7f0000",
            linewidth=1.8,
            linestyle=":",
            label=f"{HEAT_THRESHOLD_C:.0f} C hazard threshold",
        ),
    ]
    fig.suptitle(
        f"One-month spring-sample diurnal response: {zone_name} (gridiv {grid})",
        x=0.02,
        ha="left",
        fontsize=16,
        weight="bold",
    )
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.55, 0.90), ncols=4, frameon=False)
    fig.subplots_adjust(top=0.76, left=0.09, right=0.88, bottom=0.12)

    png = DOCS / "seasonal_diurnal_high_risk_zone.png"
    svg = DOCS / "seasonal_diurnal_high_risk_zone.svg"
    fig.savefig(png, dpi=220, bbox_inches="tight")
    fig.savefig(svg, bbox_inches="tight")
    plt.close(fig)
    return png


def plot_energy_balance(hourly: pd.DataFrame, neighbourhoods: pd.DataFrame, zones: dict[str, int]) -> Path:
    present_day = hourly[
        hourly["scenario"].eq("present")
        & hourly["after_spinup"]
        & hourly["hour"].between(8, 18)
    ]
    energy = present_day.groupby("gridiv")[["QN", "QH", "QE", "QS", "T2"]].mean()
    energy = neighbourhoods.set_index("gridiv").join(energy).reset_index()
    energy = energy.sort_values("bldgs")

    x = np.arange(len(energy))
    fig, ax = plt.subplots(figsize=(13, 7), constrained_layout=True)
    components = [
        ("QH", "#d73027", "QH sensible"),
        ("QE", "#1a9850", "QE latent"),
        ("QS", "#fdae61", "QS storage"),
    ]
    bottom = np.zeros(len(energy))
    for col, color, label in components:
        values = energy[col].to_numpy(dtype=float)
        ax.bar(x, values, bottom=bottom, color=color, label=label, width=0.74)
        bottom = bottom + values

    ax.scatter(
        x,
        energy["QN"],
        color="#252525",
        marker="D",
        s=44,
        zorder=5,
        label="QN net radiation",
    )

    built_grid = zones["most_built_core"]
    veg_grid = zones["most_vegetated_suburban"]
    for idx, row in energy.reset_index(drop=True).iterrows():
        if int(row["gridiv"]) == built_grid:
            ax.bar(idx, bottom[idx], width=0.84, fill=False, edgecolor="#111111", linewidth=2.3)
        if int(row["gridiv"]) == veg_grid:
            ax.bar(idx, bottom[idx], width=0.84, fill=False, edgecolor="#006d2c", linewidth=2.3)

    labels = [
        f"{row.name}\n{row.type}, bldg {row.bldgs:.2f}"
        for row in energy.itertuples(index=False)
    ]
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=42, ha="right")
    ax.set_ylabel("Mean daytime flux (W m$^{-2}$)")
    ax.set_title(
        "Present-day surface energy balance by land-cover zone",
        loc="left",
        fontsize=14,
        weight="bold",
    )
    ax.grid(True, axis="y", color="#d9d9d9", linewidth=0.8, alpha=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, ncols=4, loc="upper left")

    png = DOCS / "energy_balance_landcover_zones.png"
    svg = DOCS / "energy_balance_landcover_zones.svg"
    fig.savefig(png, dpi=220, bbox_inches="tight")
    fig.savefig(svg, bbox_inches="tight")
    plt.close(fig)

    energy.to_csv(DOCS / "energy_balance_landcover_zones.csv", index=False)
    return png


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    neighbourhoods = load_neighbourhoods()
    zones = select_contrast_zones(neighbourhoods)

    print("Selected contrast zones:")
    for key, grid in zones.items():
        row = neighbourhoods.loc[neighbourhoods["gridiv"].eq(grid)].iloc[0]
        print(
            f"  {key}: gridiv {grid}, {row['name']} "
            f"(type={row['type']}, bldgs={row['bldgs']:.3f}, green+blue={row['green_blue_fraction']:.3f})"
        )

    present_results, present_forcing = run_scenario("present")
    future_results, future_forcing = run_scenario("future_plus_2p5c", FUTURE_FORCING)

    hourly = pd.concat(
        [
            hourly_from_results("present", present_results),
            hourly_from_results("future_plus_2p5c", future_results),
        ],
        ignore_index=True,
    )
    first_time = hourly["time"].min()
    spinup_end = first_time + pd.Timedelta(days=SPINUP_DAYS)
    hourly["after_spinup"] = hourly["time"].ge(spinup_end)
    hourly["hour"] = hourly["time"].dt.hour
    hourly = hourly.merge(
        neighbourhoods[
            [
                "gridiv",
                "name",
                "type",
                "paved",
                "bldgs",
                "green_fraction",
                "green_blue_fraction",
                "impervious_fraction",
            ]
        ],
        on="gridiv",
        how="left",
    )
    hourly.to_csv(DOCS / "hourly_fluxes_t2_present_future.csv", index=False)

    risk = risk_table(hourly, neighbourhoods)
    risk.to_csv(DOCS / "risk_zone_summary.csv", index=False)
    matrix = heat_risk_matrix(hourly, neighbourhoods)
    neighbourhoods.to_csv(DOCS / "landcover_zone_summary.csv", index=False)
    pd.DataFrame(
        [
            forcing_summary("present", present_forcing),
            forcing_summary("future_plus_2p5c", future_forcing),
        ]
    ).to_csv(DOCS / "meteorology_summary.csv", index=False)

    diurnal_png = plot_diurnal(hourly, risk)
    seasonal_png = plot_seasonal_diurnal(hourly, risk)
    risk_matrix_png = plot_heat_risk_matrix(matrix)
    balance_png = plot_energy_balance(hourly, neighbourhoods, zones)

    high_risk = risk.sort_values("risk_rank").iloc[0]
    summary = {
        "spinup_days": SPINUP_DAYS,
        "analysis_days": ANALYSIS_DAYS,
        "heat_threshold_c": HEAT_THRESHOLD_C,
        "most_built_core": zones["most_built_core"],
        "most_vegetated_suburban": zones["most_vegetated_suburban"],
        "high_risk_gridiv": int(high_risk["gridiv"]),
        "high_risk_name": str(high_risk["name"]),
        "diurnal_plot": diurnal_png.name,
        "seasonal_diurnal_plot": seasonal_png.name,
        "risk_matrix_plot": risk_matrix_png.name,
        "energy_balance_plot": balance_png.name,
    }
    (DOCS / "analysis_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("High-risk zone:", f"gridiv {summary['high_risk_gridiv']}, {summary['high_risk_name']}")
    print("Wrote:", diurnal_png)
    print("Wrote:", seasonal_png)
    print("Wrote:", risk_matrix_png)
    print("Wrote:", balance_png)
    print("Wrote extracted hourly data:", DOCS / "hourly_fluxes_t2_present_future.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
