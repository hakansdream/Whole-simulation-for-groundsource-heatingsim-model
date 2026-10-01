# Solar-assisted ground-source heat pump with PCM storage for greenhouse heating

**M.Sc. thesis, Uludağ University, Department of Mechanical Engineering, Bursa, Turkey**<br>
*Investigation of the feasibility of using a solar-assisted ground-source heat pump for greenhouse heating in Bursa*<br>
Author: **Hakan Karademir** · Supervisor: **Prof. Dr. Abdulvahap Yiğit**

A 40 m² tomato greenhouse in Bursa is heated through the winter (1 October 2013 – 31 March 2014) by 30 m² of solar collectors, a latent-heat store filled with calcium chloride hexahydrate (CaCl₂·6H₂O), and a 10 kW horizontal ground-source heat pump. This repository turns the thesis into a reproducible open model: the hourly calculation is rebuilt in Python, checked against every published table it can be checked against, and documented with its data, figures and an Amesim build guide.

## Key results

| Result | Thesis | This model |
| --- | --- | --- |
| Season heat demand (greenhouse at 18 °C) | 16 748 kWh | 16 748 kWh |
| Peak heat loss | 9.58 kW, 16 Dec 2013 06:00 | 9.59 kW, 16 Dec 2013 06:00 |
| Heat from the heat pump (condenser) | 10 820 kWh | 10 821 kWh |
| Compressor electricity | 2 626 kWh | 2 626 kWh |
| Heat-pump operating hours | 2 265 h of 4 368 h | 2 265 h |
| Monthly COP, Oct → Mar | 5.28, 4.79, 4.07, 3.67, 3.92, 4.38 | same |
| Soil temperature at 1 m | 7.35–20.59 °C | 7.35–20.59 °C |
| Capital cost | 21 679 TL | 21 679 TL |
| Payback vs diesel / fuel-oil / coal boiler | 36 / 126 / 158 months | 36 / 126 / 158 months |
| Peak energy in the PCM store | 150.3 kWh | 108.5 kWh ([see notes](docs/thesis-errata.md#1-storage-peak-and-pcm-volume)) |

Over the season, solar heat covers **35 %** of the demand (direct use plus storage) and the heat pump covers **65 %** with a seasonal COP of **4.12**.

## The system

<img src="figures/thesis/fig3-1_system_schematic.png" alt="Schematic of the solar-assisted ground-source heat-pump system" width="560">

*Figure 3.1 of the thesis. Hot water from the solar collectors heats the greenhouse directly; any surplus is stored in the PCM unit for the night. When solar heat and stored heat are not enough, the heat pump runs, taking heat from a horizontal ground heat exchanger.*

| Component | Design |
| --- | --- |
| Greenhouse | 8 m × 5 m gable roof, 2.5 m walls, 1.5 m roof rise; double-layer PE cover, R = 0.26 m²K/W; set point 18 °C (tomato) |
| Solar collectors | 30 m² flat plate (17 × 1.8 m²), south-facing, 35° tilt; seasonal efficiency 0.35, system efficiency 0.70 |
| Heat pump | 10 kW heating, condenser 40 °C (water 38/27 °C), evaporator −2 to 10 °C by month |
| Ground heat exchanger | 6 modules × 95 m of ¾" PE pipe (570 m), 1 m deep, 0.5 m/s water velocity |
| Thermal storage | CaCl₂·6H₂O, melting point 29 °C, latent heat 187 kJ/kg; 1.94 m³ PCM in a 2.14 m³ unit |

<img src="figures/thesis/fig3-2_greenhouse_geometry.png" alt="3D view of the greenhouse with dimensions" width="520">

## Method in brief

The model is an hourly energy balance over 4 368 hours, using measured hourly weather data for Bursa (Turkish State Meteorological Service). Full equations: [docs/methodology.md](docs/methodology.md).

1. **Heat loss** of the greenhouse from the hourly outdoor temperature, Eq. (3.1), UA = 448 W/K.
2. **Useful solar heat** from the irradiance on the 35° collector plane, Eqs. (2.1)–(2.4), (3.6).
3. **Soil temperature** at 1 m from the periodic heat-conduction solution, Eq. (2.23).
4. **Heat-pump COP** for each month from the refrigerant cycle, Eqs. (2.9)–(2.14).
5. **Dispatch**, every hour: solar heat first, then the PCM store, then the heat pump.
6. **Ground loop**: pipe length from Eq. (3.2) and heat extraction from Eq. (2.24).
7. **Economics**: capital cost plus present-worth running cost, compared with diesel, fuel-oil and coal boilers.

## Results

### Heat demand

![Hourly greenhouse heat loss](figures/heat_loss_hourly.png)

The demand peaks in mid-December. Negative values are warm hours, when the greenhouse needs no heat.

### Where the heat comes from

![Monthly energy balance](figures/monthly_energy_balance.png)

| Month | Outdoor mean (°C) | Demand (kWh) | Solar direct (kWh) | From PCM store (kWh) | Heat pump (kWh) | Electricity (kWh) | COP | HP hours |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Oct 2013 | 12.9 | 1 868 | 221 | 982 | 664 | 126 | 5.28 | 165 |
| Nov 2013 | 11.5 | 2 149 | 280 | 696 | 1 173 | 245 | 4.79 | 308 |
| Dec 2013 | 4.9 | 4 371 | 771 | 149 | 3 451 | 848 | 4.07 | 600 |
| Jan 2014 | 9.0 | 3 015 | 500 | 388 | 2 126 | 579 | 3.67 | 466 |
| Feb 2014 | 8.6 | 2 850 | 477 | 476 | 1 897 | 484 | 3.92 | 377 |
| Mar 2014 | 10.7 | 2 496 | 372 | 615 | 1 509 | 344 | 4.38 | 349 |
| **Season** | **9.6** | **16 748** | **2 621** | **3 307** | **10 821** | **2 626** | **4.12** | **2 265** |

In October solar heat covers almost two thirds of the demand. In December, the coldest and darkest month, it covers only a fifth.

![Daily solar heat compared with the heat demand](figures/solar_vs_demand_daily.png)

### Heat pump and ground

![Monthly COP](figures/cop_monthly.png)

![Daily outdoor and soil temperatures](figures/temperatures_daily.png)

The ground at 1 m cools from 20.6 °C in October to 7.4 °C in late January, so the evaporator temperature and the COP fall with it. At the design flow (0.175 kg/s per module) the ground loop gives enough heat in all but 19 hours; in those hours the flow must rise, to at most 0.755 kg/s per module.

### Thermal storage

![Energy stored in the PCM unit](figures/storage_state_hourly.png)

The store fills on sunny days and empties at night. It holds the most energy in October, when sunny days and mild nights leave a surplus. Replayed hour by hour with the published inputs, the peak is 108.5 kWh, below the 150.3 kWh used for sizing in the thesis. The thesis volume therefore has a comfortable margin; with the reproduced peak the PCM volume would be 1.40 m³ instead of 1.94 m³.

### Economics

| Capital cost item | TL |
| --- | --- |
| Ground-loop pipe (570 m, incl. labour and fittings) | 2 009 |
| Excavation (285 m³) | 2 280 |
| PCM (1.94 m³ CaCl₂·6H₂O) | 1 990 |
| Solar collectors (17 units) | 3 400 |
| Heat pump, 10 kW | 12 000 |
| **Total** | **21 679** |

![Cost comparison with conventional boilers](figures/cost_comparison.png)

The system costs more to install but much less to run. It pays back in 36 months against a diesel boiler, 126 months against a fuel-oil boiler and 158 months against a coal boiler. Prices are 2013–2016 Turkish lira, so the curves show the method, not today's costs.

## Conclusions

* A solar-assisted horizontal GSHP with a PCM store can keep a 40 m² greenhouse in Bursa at 18 °C through the whole winter.
* The heat pump supplies about two thirds of the heat at a seasonal COP of 4.1; solar heat supplies the rest, much of it through the store.
* The higher capital cost is recovered in 3 years against diesel heating, and within the 15-year horizon of the analysis against fuel oil (10.5 years) and coal (13 years).
* The cost advantage grows in regions with colder winters, where the heat demand is higher.

## Limitations and possible next steps

* **Ideal storage.** The PCM store has no size limit, no heat loss and perfect heat transfer. A melting point of 29 °C leaves only about 10 K to heat an 18 °C greenhouse, so the real heat exchangers matter. Level B of the [Amesim guide](docs/amesim-model.md) is a first step.
* **Fixed monthly COP.** The COP depends on the month only, not on the hourly ground-loop temperature or the part load.
* **Constant ground-loop inlet temperature** (2 °C) and a simplified heat-extraction model; ground cooling over several seasons is not included.
* **Tilt factor on total radiation.** R_b is applied to global irradiation, which overestimates the collector gain at low sun angles. An isotropic-sky model (Liu–Jordan or HDKR) would be more accurate.
* **No solar gain through the cover** and no thermal mass in the greenhouse heat loss.
* **Prices** are from the original market survey (2013–2016).

## Reproduce the results

```bash
git clone <this repository>
cd <repository folder>
pip install -r requirements.txt
python scripts/run_all.py      # writes results/*.csv, results/key_results.json and figures/*.png
pytest                         # checks the model against the thesis tables
```

Python 3.9 or newer. The run takes a few seconds.

## Repository structure

```
├── README.md                  this report
├── data/                      hourly weather inputs and published thesis values (see data/README.md)
├── src/greenhouse_gshp/       the model
│   ├── parameters.py          every design value from the thesis
│   ├── physics.py             one function per thesis equation
│   └── simulation.py          hourly energy balance, summaries, economics
├── scripts/run_all.py         runs everything and draws the figures
├── results/                   hourly, daily (Tables 4.2–4.7) and monthly results, cost curves
├── figures/                   generated charts; figures/thesis/ holds original thesis figures
├── docs/
│   ├── methodology.md         equations, inputs and reproduction checks
│   ├── amesim-model.md        how to rebuild the system in Simcenter Amesim
│   └── thesis-errata.md       small issues found while reproducing the thesis
└── tests/                     pytest checks against the published numbers
```

## Citation

If you use this work, please cite the thesis (see also [CITATION.cff](CITATION.cff)):

> Karademir, H. (2016). *Investigation of the feasibility of using a solar-assisted ground-source heat pump for greenhouse heating in Bursa* (M.Sc. thesis). Uludağ University, Graduate School of Natural and Applied Sciences, Department of Mechanical Engineering, Bursa, Turkey.

## License

The code is released under the [MIT License](LICENSE). The text, figures and data in this repository are shared under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The weather data come from the Turkish State Meteorological Service (DMİGM).
