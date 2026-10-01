"""Component equations of the thesis, one function per equation.

Equation numbers refer to the M.Sc. thesis.
"""

from __future__ import annotations

import math

import numpy as np

from .parameters import Economics, Greenhouse, Ground, HeatPump, SolarCollector, Storage

# --------------------------------------------------------------------------
# Greenhouse
# --------------------------------------------------------------------------


def greenhouse_heat_loss_W(t_out_C, gh: Greenhouse = Greenhouse()):
    """Eq. (3.1): Qs = (A1/R1 + A2/R2)(Ti - Td) fw fc fs.

    The result is negative when the outdoor air is warmer than the set point;
    the energy balance treats those hours as zero demand.
    """
    return gh.ua_W_K * (gh.t_indoor_C - np.asarray(t_out_C, dtype=float))


def outdoor_temperature_from_loss_C(loss_W, gh: Greenhouse = Greenhouse()):
    """Inverse of Eq. (3.1); used to recover the hourly outdoor temperature."""
    return gh.t_indoor_C - np.asarray(loss_W, dtype=float) / gh.ua_W_K


# --------------------------------------------------------------------------
# Solar
# --------------------------------------------------------------------------


def declination_deg(day_of_year):
    """Eq. (2.1), Cooper's equation."""
    n = np.asarray(day_of_year, dtype=float)
    return 23.45 * np.sin(np.radians(360.0 * (284.0 + n) / 365.0))


def hour_angle_deg(hour):
    """Eq. (2.2): omega = 15 (12 - solar time). The thesis uses the clock hour."""
    return 15.0 * (12.0 - np.asarray(hour, dtype=float))


def geometric_factor(day_of_year, hour, sc: SolarCollector = SolarCollector(), clip: bool = False):
    """Eq. (2.4): Rb for a south-facing surface in the northern hemisphere.

    With clip=True, Rb is set to 0 when the sun is below the horizon at the
    clock hour (cos(theta_z) <= 0); the raw formula is negative there.
    """
    d = np.radians(declination_deg(day_of_year))
    w = np.radians(hour_angle_deg(hour))
    p = math.radians(sc.latitude_deg)
    pb = math.radians(sc.latitude_deg - sc.tilt_deg)
    num = np.cos(pb) * np.cos(d) * np.cos(w) + np.sin(pb) * np.sin(d)
    den = np.cos(p) * np.cos(d) * np.cos(w) + np.sin(p) * np.sin(d)
    rb = num / den
    if clip:
        rb = np.where(den > 0, np.maximum(rb, 0.0), 0.0)
    return rb


def collector_useful_heat_Wh(i_tilted_Wh_m2, sc: SolarCollector = SolarCollector()):
    """Eq. (3.6): Q = Ac * IT * eta_col * eta_m."""
    return sc.area_m2 * np.asarray(i_tilted_Wh_m2, dtype=float) * sc.eta_collector * sc.eta_system


# --------------------------------------------------------------------------
# Heat pump
# --------------------------------------------------------------------------


def heat_pump_cycle(month: int, hp: HeatPump = HeatPump()) -> dict:
    """Eqs. (2.9)-(2.14) for one month: specific enthalpies, work and COP."""
    h1 = hp.h1_kJ_kg[month]
    h2s = hp.h2s_kJ_kg[month]
    h3 = h4 = hp.h3_kJ_kg
    h2 = h1 + (h2s - h1) / hp.eta_isentropic  # Eq. (2.9)
    eta_total = hp.eta_isentropic * hp.eta_mechanical * hp.eta_belt * hp.eta_motor
    w_k = (h2s - h1) / eta_total  # Eq. (2.13), electrical work per kg
    q_cond = h2 - h3  # Eq. (2.10)
    q_evap = h1 - h4  # Eq. (2.11)
    return {
        "month": month,
        "evaporator_temp_C": hp.evaporator_temp_C[month],
        "h1": h1,
        "h2s": h2s,
        "h2": h2,
        "h3": h3,
        "h4": h4,
        "w_k_kJ_kg": w_k,
        "q_cond_kJ_kg": q_cond,
        "q_evap_kJ_kg": q_evap,
        "cop_exact": q_cond / w_k,  # Eq. (2.14)
        "cop": round(q_cond / w_k, hp.cop_decimals) if hp.cop_decimals is not None else q_cond / w_k,
        "carnot_cop": (hp.condenser_temp_C + 273.15)
        / (hp.condenser_temp_C - hp.evaporator_temp_C[month]),  # Eq. (2.6)
    }


# --------------------------------------------------------------------------
# Ground and ground heat exchanger
# --------------------------------------------------------------------------


def soil_temperature_C(day_index, g: Ground = Ground()):
    """Eq. (2.23): periodic soil temperature at depth x (cgs units, as in the thesis)."""
    period_s = 365 * 24 * 3600
    k = g.depth_cm * math.sqrt(math.pi / (g.diffusivity_cm2_s * period_s))
    t_star = np.asarray(day_index, dtype=float)
    return g.t_mean_surface_C + g.t_amplitude_C * math.exp(-k) * np.cos(
        2 * math.pi * t_star / 365.0 - k
    )


def module_mass_flow_kg_s(g: Ground = Ground()) -> float:
    """Eq. (2.25): m = rho u pi di^2 / 4 (0.1748 kg/s)."""
    return g.water_density_kg_m3 * g.water_velocity_m_s * math.pi * g.pipe_inner_diameter_m**2 / 4


def ground_heat_W(t_soil_C, m_kg_s, g: Ground = Ground()):
    """Eq. (2.24): heat from the ground to the water for n modules."""
    mcp = np.asarray(m_kg_s, dtype=float) * g.water_cp_J_kgK
    ntu = g.conductivity_W_mK * g.f_z * g.module_length_heat_m / mcp
    return g.n_modules * mcp * (np.asarray(t_soil_C) - g.inlet_water_temp_C) * (1 - np.exp(-ntu))


def ground_heat_limit_W(t_soil_C, g: Ground = Ground()):
    """Upper limit of Eq. (2.24) when the flow rate goes to infinity."""
    return g.n_modules * g.conductivity_W_mK * g.f_z * g.module_length_heat_m * (
        np.asarray(t_soil_C) - g.inlet_water_temp_C
    )


def required_module_flow_kg_s(q_evap_W: float, t_soil_C: float, g: Ground = Ground()) -> float:
    """Solve Eq. (2.24) for m (bisection), as in the 3 February example.

    Returns the design flow if it is enough, and NaN if no finite flow can
    deliver q_evap_W (the demand is above ground_heat_limit_W).
    """
    m0 = module_mass_flow_kg_s(g)
    if q_evap_W <= ground_heat_W(t_soil_C, m0, g):
        return m0
    if q_evap_W >= ground_heat_limit_W(t_soil_C, g):
        return float("nan")
    lo, hi = m0, m0
    while ground_heat_W(t_soil_C, hi, g) < q_evap_W:
        hi *= 2
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if ground_heat_W(t_soil_C, mid, g) < q_evap_W:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def ghx_length_per_kW_m(cop: float, f_heating: float, g: Ground = Ground()) -> float:
    """Eq. (3.2): required pipe length per kW of heat-pump capacity."""
    return (
        572
        * ((cop - 1) / cop)
        * (g.r_pipe_mK_W + g.r_soil_mK_W * f_heating)
        / (g.t_soil_min_C - g.t_water_min_C)
    )


# --------------------------------------------------------------------------
# Latent-heat storage
# --------------------------------------------------------------------------


def pcm_sizing(peak_energy_kWh: float, st: Storage = Storage()) -> dict:
    """Eq. (3.7) with the thesis safety (15 %) and container (10 %) margins."""
    design_kWh = peak_energy_kWh * st.safety_factor
    v_pcm = design_kWh * 3600 / (st.density_kg_m3 * st.latent_heat_kJ_kg)
    return {
        "peak_energy_kWh": peak_energy_kWh,
        "design_energy_kWh": design_kWh,
        "pcm_volume_m3": v_pcm,
        "pcm_mass_kg": v_pcm * st.density_kg_m3,
        "storage_volume_m3": v_pcm * st.container_factor,
    }


# --------------------------------------------------------------------------
# Economics (Section 4.2)
# --------------------------------------------------------------------------


def present_worth_factor(months, monthly_interest: float = 0.10 / 12):
    """Series present-worth factor used in Eqs. (4.7) and (4.9)."""
    i = monthly_interest
    v = np.asarray(months, dtype=float)
    return ((1 + i) ** v - 1) / ((1 + i) ** v * i)


def capital_cost_TL(
    pcm_volume_m3: float | None = None,
    e: Economics = Economics(),
    g: Ground = Ground(),
    sc: SolarCollector = SolarCollector(),
    st: Storage = Storage(),
) -> dict:
    """Eq. (4.1): pipe + heat pump + collectors + PCM + excavation."""
    v_pcm = e.pcm_volume_thesis_m3 if pcm_volume_m3 is None else pcm_volume_m3
    n_coll = math.ceil(sc.area_m2 / sc.unit_area_m2)
    parts = {
        "ground_loop_pipe": g.module_length_m * g.n_modules * e.pipe_price_TL_m * e.pipe_other_factor,
        "heat_pump": e.heat_pump_price_TL,
        "solar_collectors": e.collector_price_TL_unit * n_coll,
        "pcm": e.pcm_price_TL_kg * v_pcm * st.density_kg_m3,
        "excavation": g.n_modules * g.module_length_m * e.burial_depth_m * e.bucket_width_m * e.excavation_TL_m3,
    }
    parts["total"] = sum(parts.values())
    return parts
