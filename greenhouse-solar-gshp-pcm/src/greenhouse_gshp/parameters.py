"""Design parameters of the thesis system.

Every value comes from the M.Sc. thesis (Chapter 3 and Section 4.2) unless the
comment says otherwise. Units are given in the attribute names.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Greenhouse:
    """Gable-roof greenhouse, 8 m x 5 m, double-layer polyethylene cover."""

    length_m: float = 8.0
    width_m: float = 5.0
    wall_height_m: float = 2.5
    roof_rise_m: float = 1.5
    roof_slope_length_m: float = 2.91
    r_cover_m2K_W: float = 0.26  # double-layer PE film with air gap (Table 3.4)
    t_indoor_C: float = 18.0  # tomato growing temperature (Table 3.5)
    f_wind: float = 1.03  # Table 3.1
    f_construction: float = 1.00  # Table 3.2
    f_system: float = 0.95  # Table 3.3

    @property
    def floor_area_m2(self) -> float:
        return self.length_m * self.width_m

    @property
    def wall_area_m2(self) -> float:
        """A1 in Eq. (3.1): side walls + end walls + gable triangles (72.5 m2)."""
        long_walls = 2 * self.length_m * self.wall_height_m
        end_walls = 2 * self.width_m * self.wall_height_m
        gables = 2 * (self.width_m * self.roof_rise_m / 2)
        return long_walls + end_walls + gables

    @property
    def roof_area_m2(self) -> float:
        """A2 in Eq. (3.1): two roof slopes (46.56 m2)."""
        return 2 * self.roof_slope_length_m * self.length_m

    @property
    def ua_W_K(self) -> float:
        """Effective heat-loss coefficient including the three factors (448.1 W/K)."""
        conductance = (self.wall_area_m2 + self.roof_area_m2) / self.r_cover_m2K_W
        return conductance * self.f_wind * self.f_construction * self.f_system


@dataclass(frozen=True)
class SolarCollector:
    """Flat-plate collector field facing south."""

    latitude_deg: float = 40.1  # Bursa
    tilt_deg: float = 35.0
    area_m2: float = 30.0
    eta_collector: float = 0.35  # seasonal efficiency, Oct-Mar (Table 3.13)
    eta_system: float = 0.70  # piping + storage efficiency
    unit_area_m2: float = 1.80  # area of one collector (Section 4.2.5)


@dataclass(frozen=True)
class HeatPump:
    """Water-to-water heat pump, 10 kW heating capacity, condenser at 40 C."""

    capacity_kW: float = 10.0
    condenser_temp_C: float = 40.0
    supply_temp_C: float = 38.0
    return_temp_C: float = 27.0
    eta_isentropic: float = 0.80
    eta_mechanical: float = 0.80
    eta_belt: float = 0.95
    eta_motor: float = 0.96
    # Monthly evaporator temperatures (Table 3.6) and refrigerant enthalpies in
    # kJ/kg read from CATT3 (Table 3.7): h1 evaporator outlet, h2s isentropic
    # compressor outlet, h3 = h4 condenser outlet / evaporator inlet.
    evaporator_temp_C: dict = field(
        default_factory=lambda: {10: 10.0, 11: 6.0, 12: 2.0, 1: -2.0, 2: 0.0, 3: 4.0}
    )
    h1_kJ_kg: dict = field(
        default_factory=lambda: {10: 404, 11: 402, 12: 399, 1: 397, 2: 398, 3: 400}
    )
    h2s_kJ_kg: dict = field(
        default_factory=lambda: {10: 423, 11: 423, 12: 424, 1: 425, 2: 424, 3: 423}
    )
    h3_kJ_kg: float = 256.0
    # The thesis uses the COP values rounded to two decimals (5.28, 4.79, ...).
    cop_decimals: int | None = 2


@dataclass(frozen=True)
class Ground:
    """Soil and horizontal ground heat exchanger (Sections 3.3 and 3.4)."""

    # Soil temperature model, Eq. (2.23)
    t_mean_surface_C: float = 17.12  # from a MATLAB fit of 20-year 5 cm data
    t_amplitude_C: float = 13.98
    day_index_1_october: int = 91  # t* counted from 3 July (warmest day)
    depth_cm: float = 100.0
    diffusivity_cm2_s: float = 0.00775  # 0.067 m2/day, "moist soil" (Table 3.9)
    conductivity_W_mK: float = 2.42
    # Heat exchanger
    n_modules: int = 6
    module_length_m: float = 95.0  # used for cost and total length (570 m)
    module_length_heat_m: float = 90.0  # length used in Eq. (2.24) in the thesis
    pipe_inner_diameter_m: float = 0.0211  # 3/4" (Table 3.12)
    pipe_outer_diameter_m: float = 0.0269
    water_velocity_m_s: float = 0.5
    inlet_water_temp_C: float = 2.0  # Ts1, assumed constant
    water_cp_J_kgK: float = 4212.5
    water_density_kg_m3: float = 1000.0
    f_z: float = 1.052554  # F(z) value used in Eq. (2.24)
    # Pipe-length design, Eq. (3.2)
    r_pipe_mK_W: float = 0.17  # Table 3.11, 3/4" horizontal
    r_soil_mK_W: float = 1.02  # value used in the worked example (text says 1.03)
    t_soil_min_C: float = 7.35
    t_water_min_C: float = 2.0


@dataclass(frozen=True)
class Storage:
    """Latent-heat storage filled with calcium chloride hexahydrate."""

    material: str = "CaCl2.6H2O"
    melting_temp_C: float = 29.0
    latent_heat_kJ_kg: float = 187.0
    density_kg_m3: float = 1710.0
    safety_factor: float = 1.15
    container_factor: float = 1.10
    peak_energy_thesis_kWh: float = 150.283  # stated in Section 3.6.1


@dataclass(frozen=True)
class Economics:
    """Prices and finance data from the thesis market survey (Turkish lira)."""

    pipe_price_TL_m: float = 2.67  # PE pipe, 25 mm class (Table 4.8)
    pipe_other_factor: float = 1.32  # labour 1.20 x fittings 1.10
    excavation_TL_m3: float = 8.0
    bucket_width_m: float = 0.50
    burial_depth_m: float = 1.0
    pcm_price_TL_kg: float = 0.6
    pcm_volume_thesis_m3: float = 1.94
    collector_price_TL_unit: float = 200.0
    heat_pump_price_TL: float = 12000.0
    electricity_TL_kWh: float = 0.3645
    annual_interest: float = 0.10
    # The thesis rounds 0.10 / 12 to 0.0083 and the monthly fuel use to 0.1 kg.
    monthly_interest: float = 0.0083
    thesis_rounding: bool = True
    horizon_months: int = 180
    kW_to_kcal_h: float = 860.0
    boilers_TL: dict = field(
        default_factory=lambda: {"diesel": 6400.0, "fuel_oil": 6400.0, "coal": 4400.0}
    )
    # lower heating value (kcal/kg), boiler efficiency, unit price (TL/kg), Table 4.10
    fuels: dict = field(
        default_factory=lambda: {
            "diesel": (10256.0, 0.84, 4.15),
            "fuel_oil": (9875.0, 0.80, 1.82),
            "coal": (7000.0, 0.65, 1.05),
        }
    )


@dataclass(frozen=True)
class System:
    greenhouse: Greenhouse = field(default_factory=Greenhouse)
    solar: SolarCollector = field(default_factory=SolarCollector)
    heat_pump: HeatPump = field(default_factory=HeatPump)
    ground: Ground = field(default_factory=Ground)
    storage: Storage = field(default_factory=Storage)
    economics: Economics = field(default_factory=Economics)


THESIS = System()

# Season: 1 October 2013 00:00 to 31 March 2014 23:00 (4368 hours)
SEASON_START = "2013-10-01 00:00"
SEASON_HOURS = 4368
SEASON_MONTHS = (10, 11, 12, 1, 2, 3)
