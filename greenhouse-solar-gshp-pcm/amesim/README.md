# Amesim input files

Input tables for the Simcenter Amesim model of the thesis (see [docs/amesim-model.md](../docs/amesim-model.md)).
Time is in seconds from 1 October 2013 00:00; the season ends at 15 724 800 s.

| File | Content | Thesis source |
| --- | --- | --- |
| `tout.data` | Hourly outdoor air temperature (°C) | DMİGM data used in Eq. (3.1) |
| `itilt.data` | Hourly irradiance on the 35° collector plane (W/m², = Wh/m² per hour) | Figure 3.10 |
| `cop.data` | Monthly heat-pump COP | Table 3.7 |
| `tsoil.data` | Daily soil temperature at 1 m (°C) | Eq. (2.23), Figure 3.8 |
| `evap_ratio_monthly.data` | Monthly ratio of evaporator to condenser heat (optional) | Table 3.7 enthalpies |
| `expected_monthly_results.csv` | Monthly results the Amesim model should give | Tables 4.2–4.7 |

Each file starts with `# Table format: 1D` and two comment lines, then two columns (time, value).
Every interval has two points, at its start and 1 s before its end, so values stay constant through
each hour, day or month (linear interpolation reproduces the thesis staircase).

Rebuild them with `python scripts/make_amesim_tables.py`.
