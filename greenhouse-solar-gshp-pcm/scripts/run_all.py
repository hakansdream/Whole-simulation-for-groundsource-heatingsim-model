"""Run the full reproduction: hourly simulation, summaries, cost curves and figures.

Usage (from the repository root):

    python scripts/run_all.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from greenhouse_gshp import physics, simulation  # noqa: E402
from greenhouse_gshp.parameters import THESIS  # noqa: E402

RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"

# Chart style: validated categorical palette (light mode), recessive grid
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e4e3df"
C1, C2, C3, C4 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"

plt.rcParams.update(
    {
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "axes.edgecolor": GRID,
        "axes.labelcolor": INK_2,
        "axes.titlecolor": INK,
        "axes.titlesize": 13,
        "axes.titleweight": "semibold",
        "axes.titlelocation": "left",
        "axes.titlepad": 12,
        "axes.labelsize": 10.5,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "xtick.color": INK_2,
        "ytick.color": INK_2,
        "xtick.labelsize": 9.5,
        "ytick.labelsize": 9.5,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "legend.frameon": False,
        "legend.fontsize": 9.5,
        "font.family": "DejaVu Sans",
        "lines.linewidth": 2,
    }
)


def _month_axis(ax):
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.grid(axis="x", visible=False)


def _save(fig, name):
    fig.tight_layout()
    fig.savefig(FIGURES / name, dpi=160)
    plt.close(fig)


def fig_heat_loss(h):
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(h["timestamp"], h["greenhouse_heat_loss_kWh"], color=C1, lw=0.6)
    ax.axhline(THESIS.heat_pump.capacity_kW, color=INK_2, lw=1, ls="--")
    ax.axhline(0, color=INK_2, lw=0.8)
    ax.text(h["timestamp"].iloc[60], 10.25, "Heat pump capacity, 10 kW", color=INK_2, fontsize=9)
    peak = h.loc[h["greenhouse_heat_loss_kWh"].idxmax()]
    ax.annotate(
        f"Peak {peak['greenhouse_heat_loss_kWh']:.2f} kW\n16 Dec 2013, 06:00",
        xy=(peak["timestamp"], peak["greenhouse_heat_loss_kWh"]),
        xytext=(40, 14),
        textcoords="offset points",
        fontsize=9,
        color=INK,
        bbox=dict(boxstyle="square,pad=0.2", fc=SURFACE, ec="none"),
        arrowprops=dict(arrowstyle="-", color=INK_2, lw=0.8),
    )
    ax.set_title("Hourly greenhouse heat loss peaks at 9.6 kW in mid-December")
    ax.set_ylabel("Heat loss (kW)")
    ax.set_ylim(-4.5, 12.5)
    _month_axis(ax)
    _save(fig, "heat_loss_hourly.png")


def fig_energy_balance(m):
    labels = pd.to_datetime(m["month"]).dt.strftime("%b\n%Y")
    parts = [
        ("solar_direct_use_kWh", "Solar heat, used directly", C1),
        ("from_storage_kWh", "Solar heat, from PCM storage", C3),
        ("condenser_heat_kWh", "Heat pump (condenser)", C2),
    ]
    fig, ax = plt.subplots(figsize=(9, 4.6))
    bottom = pd.Series(0.0, index=m.index)
    for col, name, color in parts:
        ax.bar(labels, m[col], bottom=bottom, color=color, label=name, width=0.62,
               edgecolor=SURFACE, linewidth=2)
        bottom = bottom + m[col]
    for x, total, share in zip(labels, bottom, m["solar_share_pct"]):
        ax.text(x, total + 60, f"{total:,.0f} kWh\nsolar {share:.0f}%", ha="center", va="bottom",
                fontsize=8.8, color=INK)
    ax.set_title("The heat pump covers 65% of the season's heat; solar covers 35%")
    ax.set_ylabel("Heat delivered to the greenhouse (kWh)")
    ax.set_ylim(0, 5200)
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper right", ncol=1)
    _save(fig, "monthly_energy_balance.png")


def fig_cop(m):
    labels = pd.to_datetime(m["month"]).dt.strftime("%b %Y")
    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.bar(labels, m["cop"], color=C1, width=0.55)
    for x, v, te in zip(labels, m["cop"], THESIS.heat_pump.evaporator_temp_C.values()):
        ax.text(x, v + 0.08, f"{v:.2f}", ha="center", fontsize=9.5, color=INK)
        ax.text(x, 0.15, f"Te {te:g} °C", ha="center", fontsize=8.5, color=SURFACE)
    ax.set_title("COP falls from 5.28 to 3.67 as the ground cools")
    ax.set_ylabel("Heating COP")
    ax.set_ylim(0, 6)
    ax.grid(axis="x", visible=False)
    _save(fig, "cop_monthly.png")


def fig_temperatures(h):
    d = h.set_index("timestamp").resample("D").mean(numeric_only=True)
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(d.index, d["outdoor_temp_C"], color=C2, lw=1.4, label="Outdoor air, daily mean")
    ax.plot(d.index, d["soil_temp_1m_C"], color=C1, lw=2, label="Soil at 1 m depth, Eq. (2.23)")
    ax.axhline(THESIS.greenhouse.t_indoor_C, color=INK_2, lw=1, ls="--")
    ax.text(d.index[95], 18.4, "Greenhouse set point, 18 °C", color=INK_2, fontsize=9)
    ax.set_title("Soil at 1 m stays between 7.4 and 20.6 °C while the air swings widely")
    ax.set_ylabel("Temperature (°C)")
    ax.set_ylim(-1, 23)
    ax.legend(loc="upper right")
    _month_axis(ax)
    _save(fig, "temperatures_daily.png")


def fig_solar(h):
    d = h.set_index("timestamp").resample("D").sum(numeric_only=True)
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(d.index, d["solar_useful_heat_kWh"], color=C3, lw=1.6, label="Useful solar heat, 30 m² collectors")
    ax.plot(d.index, d["heat_demand_kWh"], color=C1, lw=1.6, label="Greenhouse heat demand")
    ax.fill_between(d.index, d["solar_useful_heat_kWh"], d["heat_demand_kWh"],
                    where=d["heat_demand_kWh"] > d["solar_useful_heat_kWh"], color=C1, alpha=0.08, lw=0)
    ax.set_title("Daily solar heat rarely matches the winter heat demand")
    ax.set_ylabel("Energy per day (kWh)")
    ax.legend(loc="upper left")
    _month_axis(ax)
    _save(fig, "solar_vs_demand_daily.png")


def fig_storage(h, peak_thesis):
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(h["timestamp"], h["storage_end_kWh"], color=C3, lw=0.9)
    ax.axhline(peak_thesis, color=C2, lw=1.2, ls="--")
    ax.text(h["timestamp"].iloc[2400], peak_thesis + 3, f"Peak stated in the thesis, {peak_thesis:.1f} kWh",
            color=INK, fontsize=9)
    i = h["storage_end_kWh"].idxmax()
    ax.annotate(
        f"Reproduced peak {h.loc[i, 'storage_end_kWh']:.1f} kWh\n17 Oct 2013, 16:00",
        xy=(h.loc[i, "timestamp"], h.loc[i, "storage_end_kWh"]),
        xytext=(30, -10),
        textcoords="offset points",
        fontsize=9,
        color=INK,
        arrowprops=dict(arrowstyle="-", color=INK_2, lw=0.8),
    )
    ax.set_title("Energy in the PCM store: charged by day, emptied most nights")
    ax.set_ylabel("Stored energy (kWh)")
    ax.set_ylim(0, 170)
    _month_axis(ax)
    _save(fig, "storage_state_hourly.png")


def fig_costs(c, payback):
    fig, ax = plt.subplots(figsize=(9, 4.4))
    series = [
        ("system_TL", "Solar-assisted GSHP", C1, 2.4),
        ("diesel_boiler_TL", "Diesel boiler", C2, 1.6),
        ("fuel_oil_boiler_TL", "Fuel-oil boiler", C3, 1.6),
        ("coal_boiler_TL", "Coal boiler", C4, 1.6),
    ]
    label_y = {"system_TL": -1.6, "diesel_boiler_TL": 0, "fuel_oil_boiler_TL": 1.2, "coal_boiler_TL": 0.2}
    for col, name, color, lw in series:
        ax.plot(c["month"], c[col] / 1000, color=color, lw=lw, label=name)
        ax.text(182, c[col].iloc[-1] / 1000 + label_y[col], name, color=INK, fontsize=9, va="center")
    for fuel, col in [("diesel", "diesel_boiler_TL"), ("fuel_oil", "fuel_oil_boiler_TL"), ("coal", "coal_boiler_TL")]:
        mth = payback[fuel]
        y = c.loc[c["month"] == mth, "system_TL"].iloc[0] / 1000
        ax.plot([mth], [y], "o", ms=7, color=INK, mec=SURFACE, mew=2, zorder=5)
        ax.text(mth, y - 3.2, f"{mth} mo", ha="center", fontsize=9, color=INK)
    ax.set_title("Payback: 36 months against diesel, 126 against fuel oil, 158 against coal")
    ax.set_xlabel("Months after installation")
    ax.set_ylabel("Capital + present-worth running cost (1000 TL)")
    ax.set_xlim(0, 215)
    ax.set_ylim(0, 65)
    ax.legend(loc="upper left")
    _save(fig, "cost_comparison.png")


def _rounded(df, digits):
    out = df.copy()
    num = out.select_dtypes("number").columns
    out[num] = out[num].round(digits)
    return out


def main():
    RESULTS.mkdir(exist_ok=True)
    FIGURES.mkdir(exist_ok=True)

    hourly = simulation.run()
    daily = simulation.daily_summary(hourly)
    monthly = simulation.monthly_summary(hourly)
    curves = simulation.cost_curves(hourly)
    key = simulation.key_results(hourly)

    _rounded(hourly, 4).to_csv(RESULTS / "hourly_results.csv", index=False)
    _rounded(daily, 3).to_csv(RESULTS / "daily_results.csv", index=False)
    monthly.round(2).to_csv(RESULTS / "monthly_results.csv", index=False)
    curves.round(2).to_csv(RESULTS / "cost_curves.csv", index=False)

    cycles = pd.DataFrame([physics.heat_pump_cycle(m) for m in (10, 11, 12, 1, 2, 3)])
    cycles.round(4).to_csv(RESULTS / "heat_pump_cycle.csv", index=False)

    sizing = {
        "thesis_peak": physics.pcm_sizing(THESIS.storage.peak_energy_thesis_kWh),
        "reproduced_peak": physics.pcm_sizing(key["storage_peak_kWh"]),
    }
    key["pcm_sizing"] = sizing
    key["capital_cost_breakdown_TL"] = physics.capital_cost_TL()
    # Eq. (3.2) with the thesis inputs: October COP and Fi = 4.77 kW / 10 kW = 0.477
    key["ghx_length_per_kW_m"] = physics.ghx_length_per_kW_m(5.28, 0.477)
    (RESULTS / "key_results.json").write_text(json.dumps(key, indent=2, default=str))

    fig_heat_loss(hourly)
    fig_energy_balance(monthly)
    fig_cop(monthly)
    fig_temperatures(hourly)
    fig_solar(hourly)
    fig_storage(hourly, THESIS.storage.peak_energy_thesis_kWh)
    fig_costs(curves, key["payback_months"])

    print(json.dumps({k: v for k, v in key.items() if not isinstance(v, dict)}, indent=2, default=str))
    print("payback:", key["payback_months"])


if __name__ == "__main__":
    main()
