"""Hourly energy balance of the solar-assisted GSHP with PCM storage.

Control logic (Chapter 3 of the thesis), applied hour by hour:

1. Solar heat from the collectors goes to the greenhouse first.
2. Any solar surplus charges the PCM storage (no capacity limit, no losses).
3. A deficit is taken from the storage first.
4. The heat pump covers what is still missing (condenser heat), with the
   monthly COP of Table 3.7.

With the thesis input data this reproduces the published seasonal totals:
condenser heat 10 820 kWh, compressor work 2 626 kWh and 2 265 operating hours.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from . import physics
from .parameters import SEASON_MONTHS, THESIS, System

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def load_inputs(path: Path | None = None) -> pd.DataFrame:
    """Hourly weather inputs for 1 Oct 2013 - 31 Mar 2014 (4368 rows)."""
    path = path or DATA_DIR / "hourly_inputs.csv"
    df = pd.read_csv(path, parse_dates=["timestamp"])
    return df


def run(
    inputs: pd.DataFrame | None = None,
    system: System = THESIS,
    recompute_tilt: bool = False,
) -> pd.DataFrame:
    """Run the hourly simulation and return one row per hour (energies in kWh).

    recompute_tilt=False uses the tilted irradiance published in the thesis
    (exact reproduction). True recomputes it from the horizontal value with
    Eq. (2.4), with Rb = 0 while the sun is below the horizon; the two differ
    only in 135 hours around 07:00 and 17:00.
    """
    df = (load_inputs() if inputs is None else inputs).copy()
    ts = df["timestamp"]
    month = ts.dt.month.to_numpy()
    doy = ts.dt.dayofyear.to_numpy()
    hour = ts.dt.hour.to_numpy()

    rb = physics.geometric_factor(doy, hour, system.solar, clip=True)
    if recompute_tilt:
        g_tilt = df["solar_horizontal_Wh_m2"].to_numpy() * rb
    else:
        g_tilt = df["solar_tilted_thesis_Wh_m2"].to_numpy()

    loss = physics.greenhouse_heat_loss_W(df["outdoor_temp_C"], system.greenhouse) / 1000
    solar = physics.collector_useful_heat_Wh(g_tilt, system.solar) / 1000
    demand = np.maximum(loss, 0.0)

    cycles = {m: physics.heat_pump_cycle(m, system.heat_pump) for m in SEASON_MONTHS}
    cop = np.array([cycles[m]["cop"] for m in month])
    evap_ratio = np.array([cycles[m]["q_evap_kJ_kg"] / cycles[m]["q_cond_kJ_kg"] for m in month])
    q_cond_specific = np.array([cycles[m]["q_cond_kJ_kg"] for m in month])

    n = len(df)
    to_storage = np.zeros(n)
    from_storage = np.zeros(n)
    condenser = np.zeros(n)
    stored_start = np.zeros(n)
    stored_end = np.zeros(n)
    e = 0.0
    for k in range(n):
        stored_start[k] = e
        if solar[k] >= demand[k]:
            to_storage[k] = solar[k] - demand[k]
            e += to_storage[k]
        else:
            need = demand[k] - solar[k]
            from_storage[k] = min(e, need)
            e -= from_storage[k]
            condenser[k] = need - from_storage[k]
        stored_end[k] = e

    compressor = condenser / cop
    evaporator = condenser * evap_ratio

    # Soil temperature: one value per day, t* counted from 3 July (Eq. 2.23)
    day_index = system.ground.day_index_1_october + (ts - ts.iloc[0]).dt.days.to_numpy()
    t_soil = np.round(physics.soil_temperature_C(day_index, system.ground), 2)

    ghx_available = physics.ground_heat_W(
        t_soil, physics.module_mass_flow_kg_s(system.ground), system.ground
    ) / 1000
    ghx_limit = physics.ground_heat_limit_W(t_soil, system.ground) / 1000
    ghx_flow = np.array(
        [
            physics.required_module_flow_kg_s(q * 1000, t, system.ground) if q > 0 else 0.0
            for q, t in zip(evaporator, t_soil)
        ]
    )

    out = pd.DataFrame(
        {
            "timestamp": ts,
            "outdoor_temp_C": df["outdoor_temp_C"],
            "soil_temp_1m_C": t_soil,
            "solar_horizontal_kWh_m2": df["solar_horizontal_Wh_m2"] / 1000,
            "geometric_factor_Rb": rb,
            "solar_tilted_kWh_m2": g_tilt / 1000,
            "solar_useful_heat_kWh": solar,  # Q_fay
            "greenhouse_heat_loss_kWh": loss,  # Q_s (negative = net gain)
            "heat_demand_kWh": demand,
            "solar_direct_use_kWh": np.minimum(solar, demand),  # Q_fay-kalan
            "auxiliary_demand_kWh": demand - np.minimum(solar, demand),  # Q_ek
            "to_storage_kWh": to_storage,  # Q_dv
            "from_storage_kWh": from_storage,  # Q_dk
            "storage_start_kWh": stored_start,  # Q_depo
            "storage_end_kWh": stored_end,
            "condenser_heat_kWh": condenser,  # Q_yog
            "evaporator_heat_kWh": evaporator,  # Q_bi
            "compressor_work_kWh": compressor,  # W_k
            "cop": cop,
            "refrigerant_flow_kg_s": condenser / q_cond_specific,  # kWh/h / (kJ/kg)
            "ghx_available_at_design_flow_kWh": ghx_available,
            "ghx_limit_kWh": ghx_limit,
            "ghx_required_module_flow_kg_s": ghx_flow,
        }
    )
    return out


def daily_summary(hourly: pd.DataFrame) -> pd.DataFrame:
    """Daily values in the format of Tables 4.2-4.7."""
    d = hourly.set_index("timestamp")
    agg = d.resample("D").agg(
        {
            "outdoor_temp_C": "mean",
            "soil_temp_1m_C": "mean",
            "solar_horizontal_kWh_m2": "sum",
            "solar_tilted_kWh_m2": "sum",
            "solar_useful_heat_kWh": "sum",
            "to_storage_kWh": "sum",
            "solar_direct_use_kWh": "sum",
            "heat_demand_kWh": "sum",
            "auxiliary_demand_kWh": "sum",
            "from_storage_kWh": "sum",
            "condenser_heat_kWh": "sum",
            "evaporator_heat_kWh": "sum",
            "compressor_work_kWh": "sum",
            "storage_end_kWh": "max",
        }
    )
    agg = agg.rename(columns={"storage_end_kWh": "storage_peak_kWh", "heat_demand_kWh": "greenhouse_heat_loss_kWh"})
    agg.index.name = "date"
    return agg.reset_index()


def monthly_summary(hourly: pd.DataFrame) -> pd.DataFrame:
    d = hourly.set_index("timestamp")
    agg = d.resample("MS").agg(
        {
            "outdoor_temp_C": "mean",
            "soil_temp_1m_C": "mean",
            "heat_demand_kWh": "sum",
            "solar_useful_heat_kWh": "sum",
            "solar_direct_use_kWh": "sum",
            "from_storage_kWh": "sum",
            "condenser_heat_kWh": "sum",
            "compressor_work_kWh": "sum",
            "cop": "mean",
        }
    )
    hours = (d["condenser_heat_kWh"] > 0).resample("MS").sum()
    agg["heat_pump_hours"] = hours
    agg["solar_share_pct"] = 100 * (agg["solar_direct_use_kWh"] + agg["from_storage_kWh"]) / agg["heat_demand_kWh"]
    agg.index = agg.index.strftime("%Y-%m")
    agg.index.name = "month"
    return agg.rename(columns={"heat_demand_kWh": "greenhouse_heat_loss_kWh"}).reset_index()


def cost_curves(hourly: pd.DataFrame, system: System = THESIS, capital: float | None = None) -> pd.DataFrame:
    """Present-worth cost of the system and the three boilers, month 1-180."""
    e = system.economics
    months = np.arange(1, e.horizon_months + 1)
    i = e.monthly_interest if e.thesis_rounding else e.annual_interest / 12
    pwf = physics.present_worth_factor(months, i)
    cap = physics.capital_cost_TL(e=e)["total"] if capital is None else capital
    if e.thesis_rounding:
        cap = round(cap)
    # Annual energy is paid in 12 equal monthly amounts (Tokgoz 2006 method)
    w_month = hourly["compressor_work_kWh"].sum() / 12
    out = {"month": months, "system_TL": cap + w_month * e.electricity_TL_kWh * pwf}
    q_kcal = hourly["heat_demand_kWh"].sum() * e.kW_to_kcal_h
    for fuel, (lhv, eff, price) in e.fuels.items():
        fuel_month = q_kcal / (lhv * eff) / 12  # Eq. (4.8), kg per month
        if e.thesis_rounding:
            fuel_month = round(fuel_month, 1)
        out[f"{fuel}_boiler_TL"] = e.boilers_TL[fuel] + fuel_month * price * pwf
    return pd.DataFrame(out)


def payback_months(curves: pd.DataFrame) -> dict:
    """First month in which the system is cheaper than each boiler."""
    res = {}
    for col in [c for c in curves.columns if c.endswith("_boiler_TL")]:
        cheaper = curves.loc[curves["system_TL"] <= curves[col], "month"]
        res[col.replace("_boiler_TL", "")] = int(cheaper.iloc[0]) if len(cheaper) else None
    return res


def key_results(hourly: pd.DataFrame, system: System = THESIS) -> dict:
    """Headline numbers, side by side with the values stated in the thesis."""
    peak = float(hourly["storage_end_kWh"].max())
    peak_time = hourly.loc[hourly["storage_end_kWh"].idxmax(), "timestamp"]
    worst = hourly.loc[hourly["greenhouse_heat_loss_kWh"].idxmax()]
    curves = cost_curves(hourly, system)
    cond = hourly["condenser_heat_kWh"]
    evap = hourly["evaporator_heat_kWh"]
    infeasible = int(((evap > hourly["ghx_limit_kWh"]) & (evap > 0)).sum())
    return {
        "season_heat_demand_kWh": float(hourly["heat_demand_kWh"].sum()),
        "peak_heat_loss_kW": float(worst["greenhouse_heat_loss_kWh"]),
        "peak_heat_loss_time": str(worst["timestamp"]),
        "solar_useful_heat_kWh": float(hourly["solar_useful_heat_kWh"].sum()),
        "solar_used_kWh": float(hourly["solar_direct_use_kWh"].sum() + hourly["from_storage_kWh"].sum()),
        "condenser_heat_kWh": float(cond.sum()),
        "compressor_work_kWh": float(hourly["compressor_work_kWh"].sum()),
        "heat_pump_hours": int((cond > 0).sum()),
        "heating_operating_factor": float(cond.sum() / (cond > 0).sum() / system.heat_pump.capacity_kW),
        "seasonal_cop": float(cond.sum() / hourly["compressor_work_kWh"].sum()),
        "storage_peak_kWh": peak,
        "storage_peak_time": str(peak_time),
        "soil_temp_1m_min_C": float(hourly["soil_temp_1m_C"].min()),
        "soil_temp_1m_max_C": float(hourly["soil_temp_1m_C"].max()),
        "hours_above_ghx_limit": infeasible,
        "capital_cost_TL": physics.capital_cost_TL(e=system.economics)["total"],
        "payback_months": payback_months(curves),
    }
