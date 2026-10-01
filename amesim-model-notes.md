# Amesim model of the M.Sc. thesis

Updated 2026-10-01.

The thesis system (Uludağ University, Bursa): 40 m² gable-roof tomato greenhouse at 18 °C; 30 m² flat-plate solar collectors; CaCl2·6H2O PCM store (29 °C, 187 kJ/kg, 1.94 m³); 10 kW water-to-water heat pump (condenser 40 °C, monthly COP 5.28-3.67); horizontal ground heat exchanger, 6 modules × 95 m of 3/4" PE at 1 m depth. Season 1 Oct 2013 - 31 Mar 2014.

Amesim build guide (Claude doc): https://claude.ai/code/artifact/e3894c7b-97cf-4d62-9ad5-66beb1cb2758 — rewritten on 2026-10-01 to match the thesis exactly (the first version used assumed values and is superseded).

- Level A: exact replica of the thesis hourly energy balance (Signal blocks + a Thermal greenhouse check). Control order: solar direct → ideal PCM store → heat pump. Inputs: amesim/tout.data, itilt.data, cop.data, tsoil.data in the GitHub project (greenhouse-solar-gshp-pcm.zip).
- Expected totals: demand 16 748 kWh, condenser 10 821 kWh, compressor 2 626 kWh, 2 265 heat-pump hours, store peak 108.5 kWh (thesis states 150.3 kWh).
- Level B: optional physical version with water loops, real PCM store and finite heat exchangers (beyond the thesis).

The same guide is in docs/amesim-model.md of the GitHub project.
