# Data

All data cover the heating season **1 October 2013 00:00 – 31 March 2014 23:00** (182 days, 4368 hours) for **Bursa Central, Turkey** (latitude 40.1° N). Hour stamps are local clock hours, as in the thesis.

## Model inputs

| File | Content | Source |
| --- | --- | --- |
| `hourly_inputs.csv` | Hourly outdoor air temperature (°C), global irradiation on a horizontal surface (Wh/m²) and on the 35° tilted collector plane as used in the thesis (Wh/m²) | Turkish State Meteorological Service (DMİGM), Bursa station, as used in the thesis |
| `soil_temperature_bursa_monthly_20yr.csv` | 20-year monthly mean soil temperatures at 5, 20, 50 and 100 cm | DMİGM, Table 3.8 of the thesis |

### How the hourly file was built

The hourly series were taken from the chart data embedded in the thesis document (Figures 3.3, 3.9 and 3.10), so they are exactly the numbers the thesis calculations used.

* **Outdoor temperature** is recovered from the hourly greenhouse heat loss (Figure 3.3) by inverting Eq. (3.1): `T_out = 18 − Q_s / 448.08 W/K`. Every recovered value falls on the 0.1 °C grid of the meteorological record.
* It agrees with **Appendix 1** of the thesis for 4291 of 4368 hours. The exceptions are three whole days (1, 2 and 25 October 2013), where the appendix table shows different numbers, and 5 single hours. The calculation used the values in this file.
* **Tilted irradiance** is the series published in Figure 3.10. It equals the horizontal value × R_b from Eq. (2.4) in 1928 of 2063 sunny hours; the other 135 hours lie around 07:00 and 17:00, where the thesis used other factors. See `docs/methodology.md`.

## Thesis reference values (`thesis_reference/`)

These files hold the published results. The tests in `tests/` compare the model against them.

| File | Thesis item |
| --- | --- |
| `fig3-3_3-9_3-10_3-11_hourly.csv` | Hourly heat loss, horizontal and tilted irradiation, and useful collector heat (Figures 3.3, 3.9, 3.10, 3.11) |
| `fig3-6_monthly_cop.csv` | Monthly evaporator temperature and COP (Table 3.6, Figure 3.6) |
| `fig3-8_daily_soil_temperature_1m.csv` | Daily soil temperature at 1 m (Figure 3.8) |
| `fig4-2_cost_curves.csv` | Present-worth cost curves, months 1–180 (Figure 4.2, Table 4.11) |
| `daily_table_samples.csv` | Seven daily rows transcribed from Tables 4.2–4.6 |

## Units and symbols used in the thesis tables

| Symbol | Meaning |
| --- | --- |
| Q_fay | Useful heat from the solar collectors |
| Q_dv | Heat supplied to the storage |
| Q_fay-kalan | Solar heat used directly in the greenhouse |
| Q_s | Greenhouse heat loss (demand) |
| Q_ek | Auxiliary heat demand after direct solar use |
| Q_dk | Heat drawn from the storage |
| Q_depo | Energy in the storage |
| Q_yoğ | Heat rejected by the condenser (heat-pump output) |
| Q_bi | Heat supplied to the evaporator (from the ground) |
| W_k | Compressor electrical work |
