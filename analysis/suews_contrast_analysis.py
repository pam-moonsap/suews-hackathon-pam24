#!/usr/bin/env python
"""Run UDA-city present/future SUEWS contrasts and create docs plots."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
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


def vulnerability_index(socio: pd.DataFrame) -> pd.Series:
    components = pd.DataFrame(
        {
            "elderly": socio["frac_over65"],
            "young": socio["frac_under5"],
            "no_ac": 1.0 - socio["ac_access"],
            "outdoor_work": socio["frac_outdoor_workers"],
            "deprivation": socio["deprivation_index"],
        },
        index=socio.index,
    )
    return minmax(components.mean(axis=1))


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


def plot_diurnal(hourly: pd.DataFrame, risk: pd.DataFrame) -> Path:
    high_risk = risk.sort_values("risk_rank").iloc[0]
    grid = int(high_risk["gridiv"])
    zone_name = str(high_risk["name"])
    subset = hourly[hourly["gridiv"].eq(grid) & hourly["after_spinup"]].copy()

    # Compute future-present changes point by point first, then summarise those
    # deltas by local hour. This preserves the paired scenario signal instead
    # of subtracting already-smoothed curves.
    cols = ["QN", "QH", "QE", "QS", "T2"]
    present = (
        subset[subset["scenario"].eq("present")]
        .set_index("time")[["hour"] + cols]
        .sort_index()
    )
    future = (
        subset[subset["scenario"].eq("future_plus_2p5c")]
        .set_index("time")[cols]
        .sort_index()
    )
    common_times = present.index.intersection(future.index)
    delta = future.loc[common_times, cols] - present.loc[common_times, cols]
    delta["hour"] = present.loc[common_times, "hour"]
    delta_out = delta.reset_index().rename(columns={"index": "time"})
    delta_out.insert(0, "name", zone_name)
    delta_out.insert(0, "gridiv", grid)
    delta_out.to_csv(DOCS / "hourly_deltas_high_risk_zone.csv", index=False)
    diurnal = delta.groupby("hour")[cols].mean().reset_index()
    diurnal.to_csv(DOCS / "diurnal_deltas_high_risk_zone.csv", index=False)

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
    axes[1].plot(
        diurnal["hour"],
        diurnal["T2"],
        label="Delta T2 air temperature",
        color="#c51b7d",
        linewidth=2.8,
    )

    axes[0].set_title(
        f"Future-minus-present diurnal response: {zone_name} (gridiv {grid})",
        loc="left",
        fontsize=14,
        weight="bold",
    )
    axes[0].set_ylabel("Flux change (W m$^{-2}$)")
    axes[1].set_ylabel("T2 change (deg C)")
    axes[1].set_xlabel("Local hour")
    axes[1].set_xticks(range(0, 24, 2))
    for ax in axes:
        ax.axhline(0, color="#777777", linewidth=1.0, alpha=0.7)
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
    neighbourhoods.to_csv(DOCS / "landcover_zone_summary.csv", index=False)
    pd.DataFrame(
        [
            forcing_summary("present", present_forcing),
            forcing_summary("future_plus_2p5c", future_forcing),
        ]
    ).to_csv(DOCS / "meteorology_summary.csv", index=False)

    diurnal_png = plot_diurnal(hourly, risk)
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
        "energy_balance_plot": balance_png.name,
    }
    (DOCS / "analysis_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("High-risk zone:", f"gridiv {summary['high_risk_gridiv']}, {summary['high_risk_name']}")
    print("Wrote:", diurnal_png)
    print("Wrote:", balance_png)
    print("Wrote extracted hourly data:", DOCS / "hourly_fluxes_t2_present_future.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
