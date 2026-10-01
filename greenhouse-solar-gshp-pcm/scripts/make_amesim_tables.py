"""Write Simcenter Amesim 1D time tables (.data) for the Level A model.

Each hourly (or daily, monthly) value is held constant over its interval,
as in the thesis. A staircase is written with two points per interval:
(t_start, v) and (t_start + dt - 1 s, v). The 1 s ramp between intervals
is negligible and avoids repeated x values, which some table readers refuse.

Usage (from the repository root):

    python scripts/make_amesim_tables.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from greenhouse_gshp import physics, simulation  # noqa: E402

OUT = ROOT / "amesim"
SEASON_END_S = 182 * 86400  # 15 724 800 s


def staircase(starts_s, values, end_s):
    rows = []
    for k, (t, v) in enumerate(zip(starts_s, values)):
        t_next = starts_s[k + 1] if k + 1 < len(starts_s) else end_s
        rows.append((t, v))
        rows.append((t_next - 1, v))
    rows.append((end_s, values[-1]))
    return rows


def write_table(name, rows, quantity, unit, note):
    path = OUT / name
    with path.open("w", newline="\n") as f:
        f.write("# Table format: 1D\n")
        f.write(f"# x: time [s] from 1 Oct 2013 00:00   y: {quantity} [{unit}]\n")
        f.write(f"# {note}\n")
        for t, v in rows:
            f.write(f"{t:d} {v:.6g}\n")
    return path


def main():
    OUT.mkdir(exist_ok=True)
    inp = simulation.load_inputs()
    t0 = inp["timestamp"].iloc[0]
    hour_s = ((inp["timestamp"] - t0).dt.total_seconds()).astype(int).tolist()

    write_table(
        "tout.data",
        staircase(hour_s, inp["outdoor_temp_C"].tolist(), SEASON_END_S),
        "outdoor air temperature",
        "degC",
        "Bursa, DMIGM hourly data as used in the thesis (Eq. 3.1 input)",
    )
    write_table(
        "itilt.data",
        staircase(hour_s, inp["solar_tilted_thesis_Wh_m2"].tolist(), SEASON_END_S),
        "irradiance on the 35 deg collector plane",
        "W/m2",
        "hourly mean = thesis Wh/m2 per hour (Figure 3.10)",
    )

    months = pd.date_range("2013-10-01", periods=6, freq="MS")
    month_s = [int((m - t0).total_seconds()) for m in months]
    cycles = [physics.heat_pump_cycle(m.month) for m in months]
    write_table(
        "cop.data",
        staircase(month_s, [c["cop"] for c in cycles], SEASON_END_S),
        "heat-pump COP",
        "-",
        "monthly values of Table 3.7",
    )
    write_table(
        "evap_ratio_monthly.data",
        staircase(month_s, [round(c["q_evap_kJ_kg"] / c["q_cond_kJ_kg"], 4) for c in cycles], SEASON_END_S),
        "evaporator heat / condenser heat",
        "-",
        "(h1-h4)/(h2-h3) from Table 3.7; Tables 4.2-4.7 use 0.8605 in every month",
    )

    day_s = [d * 86400 for d in range(182)]
    tsoil = physics.soil_temperature_C([91 + d for d in range(182)])
    write_table(
        "tsoil.data",
        staircase(day_s, [round(float(x), 2) for x in tsoil], SEASON_END_S),
        "soil temperature at 1 m",
        "degC",
        "Eq. (2.23), one value per day as in Figure 3.8",
    )

    hourly = simulation.run()
    monthly = simulation.monthly_summary(hourly)
    monthly["evaporator_heat_thesis_ratio_kWh"] = (
        hourly.set_index("timestamp")["condenser_heat_kWh"].resample("MS").sum().to_numpy() * 148 / 172
    )
    num = monthly.select_dtypes("number").columns
    monthly[num] = monthly[num].round(2)
    monthly.to_csv(OUT / "expected_monthly_results.csv", index=False)
    print("written:", sorted(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    main()
