"""Check that the model reproduces the numbers published in the thesis."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from greenhouse_gshp import physics, simulation

REF = Path(__file__).resolve().parents[1] / "data" / "thesis_reference"


@pytest.fixture(scope="module")
def hourly():
    return simulation.run()


def test_greenhouse_heat_loss_worked_example():
    # Section 3.1.1: 1 Oct 2013 00:00, Td = 8 C -> 4480 W
    assert physics.greenhouse_heat_loss_W(8.0) == pytest.approx(4480.8, abs=0.5)


def test_hourly_heat_loss_and_solar_match_published_figures(hourly):
    ref = pd.read_csv(REF / "fig3-3_3-9_3-10_3-11_hourly.csv")
    loss = hourly["greenhouse_heat_loss_kWh"].to_numpy() * 1000
    solar = hourly["solar_useful_heat_kWh"].to_numpy() * 1000
    assert np.abs(loss - ref["fig3_3_greenhouse_heat_loss_Wh"]).max() < 0.01
    assert np.abs(solar - ref["fig3_11_collector_useful_heat_Wh"]).max() < 0.01


def test_soil_temperature_matches_figure_3_8(hourly):
    ref = pd.read_csv(REF / "fig3-8_daily_soil_temperature_1m.csv")
    model = hourly.set_index("timestamp")["soil_temp_1m_C"].resample("D").first().to_numpy()
    assert np.abs(model - ref["soil_temperature_1m_C"]).max() < 0.011


def test_monthly_cop_table_3_7():
    cops = [physics.heat_pump_cycle(m)["cop"] for m in (10, 11, 12, 1, 2, 3)]
    assert cops == [5.28, 4.79, 4.07, 3.67, 3.92, 4.38]


def test_seasonal_totals(hourly):
    k = simulation.key_results(hourly)
    assert k["season_heat_demand_kWh"] == pytest.approx(16748, abs=1)  # Chapter 5
    assert k["condenser_heat_kWh"] == pytest.approx(10820, abs=1)  # Section 3.4
    assert k["compressor_work_kWh"] == pytest.approx(2626.457, abs=0.01)  # Section 4.2.8
    assert k["heat_pump_hours"] == 2265
    assert k["peak_heat_loss_kW"] == pytest.approx(9.58, abs=0.01)
    assert k["peak_heat_loss_time"].startswith("2013-12-16 06:00")


@pytest.mark.parametrize(
    "col_model,col_ref",
    [
        ("solar_useful_heat_kWh", "Q_fay_kWh"),
        ("to_storage_kWh", "Q_dv_kWh"),
        ("solar_direct_use_kWh", "Q_fay_kalan_kWh"),
        ("greenhouse_heat_loss_kWh", "Q_s_kWh"),
        ("auxiliary_demand_kWh", "Q_ek_kWh"),
        ("from_storage_kWh", "Q_dk_kWh"),
        ("condenser_heat_kWh", "Q_yog_kWh"),
        ("compressor_work_kWh", "W_k_kWh"),
    ],
)
def test_daily_tables_4_2_to_4_6(hourly, col_model, col_ref):
    ref = pd.read_csv(REF / "daily_table_samples.csv", parse_dates=["date"])
    daily = simulation.daily_summary(hourly).set_index("date")
    model = daily.loc[ref["date"], col_model].to_numpy()
    assert np.abs(model - ref[col_ref].to_numpy()).max() < 0.002


def test_cost_curves_and_payback(hourly):
    ref = pd.read_csv(REF / "fig4-2_cost_curves.csv")
    curves = simulation.cost_curves(hourly)
    diff = np.abs(curves.iloc[:, 1:].to_numpy() - ref.iloc[:, 1:].to_numpy())
    assert diff.max() < 0.05
    assert simulation.payback_months(curves) == {"diesel": 36, "fuel_oil": 126, "coal": 158}


def test_capital_cost_section_4_2_7():
    cost = physics.capital_cost_TL()
    assert round(cost["ground_loop_pipe"]) == 2009
    assert round(cost["excavation"]) == 2280
    assert round(cost["pcm"]) == 1990
    assert cost["solar_collectors"] == 3400
    assert round(cost["total"]) == 21679


def test_ground_heat_exchanger_design():
    assert physics.module_mass_flow_kg_s() == pytest.approx(0.1748, abs=1e-4)
    assert physics.ghx_length_per_kW_m(5.28, 0.477) == pytest.approx(56.90, abs=0.01)
    # 3 February, 06:00 example: 6.600 kW available, 7.398 kW needed -> 0.7350 kg/s
    assert physics.ground_heat_W(7.58, physics.module_mass_flow_kg_s()) == pytest.approx(6600, abs=10)
    assert physics.required_module_flow_kg_s(7398, 7.58) == pytest.approx(0.735, abs=0.001)


def test_pcm_sizing_section_3_6_1():
    s = physics.pcm_sizing(150.283)
    assert s["pcm_volume_m3"] == pytest.approx(1.94, abs=0.01)
    assert s["storage_volume_m3"] == pytest.approx(2.14, abs=0.01)
