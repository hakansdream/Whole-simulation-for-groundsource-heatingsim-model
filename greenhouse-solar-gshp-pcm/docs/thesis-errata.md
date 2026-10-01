# Notes on the thesis text and tables

Rebuilding every calculation in code made some small problems in the English edition of the thesis visible. None of them changes the main conclusions: the COP values, the season totals and the payback periods all reproduce exactly. They are listed here so that readers of the thesis and of this repository see the same numbers.

## 1. Storage peak and PCM volume

| Quantity | Thesis (Section 3.6.1) | This model |
| --- | --- | --- |
| Peak energy in the store | 150.283 kWh | 108.51 kWh (17 Oct 2013, 16:00) |
| Design energy (+15 %) | 173 kWh | 124.8 kWh |
| PCM volume | 1.94 m³ | 1.40 m³ |
| Storage volume (+10 %) | 2.14 m³ | 1.55 m³ |
| PCM cost | 1 990 TL | 1 441 TL |
| Capital cost | 21 679 TL | 21 130 TL |
| Payback vs diesel / fuel oil / coal | 36 / 126 / 158 months | 35 / 118 / 148 months |

The model matches every published daily value of heat to and from the store (Tables 4.2–4.6), so the charging and discharging logic is the same. The 150.283 kWh peak could not be reproduced from those values; it may come from a different version of the original spreadsheet. The published sizing is on the safe side. The repository keeps the thesis value (1.94 m³) for the capital cost, so the payback periods in the README stay those of the thesis.

## 2. Table 4.7 (March) shows the February table

The English document embeds the same picture for Table 4.6 (February) and Table 4.7 (March). The March daily values are rebuilt in `results/daily_results.csv`.

## 3. A find-and-replace changed "ay" into "month" inside words

In the English text, the letters "ay" inside words were replaced by "month" (Turkish *ay* = month). This affects 98 words, including the abstract and the conclusions.

| Printed | Should be | Count |
| --- | --- | --- |
| dmonth, dmonths | day, days | 41 |
| mmonth, MMONTH | may, MAY (Table 3.8) | 20 |
| lmonther, lmonthers | layer, layers | 10 |
| pmonthback, pay monthback | payback | 8 |
| pmonths (for itself) | pays | 5 |
| alwmonths | always | 3 |
| Q_fmonth | Q_fay | 3 |
| todmonth | today | 2 |
| dmonthtime, dmonthlight | daytime, daylight | 2 |
| wmonth, wmonths | way, ways | 2 |
| rmonths | rays | 1 |
| clmonth | clay | 1 |

A case-insensitive search for the regular expression `[a-z]month|monthback` finds all of them, including the unit "m²/dmonth" (m²/day) in Table 3.9.

## 4. Smaller inconsistencies

| Place | Issue |
| --- | --- |
| Section 3.4 | The text gives R_t = 1.03 m·K/W; the worked example uses 1.02. With 1.03, L₁ = 57.31 m/kW instead of 56.90. |
| Sections 3.4 and 4.2.2 | The modules are 95 m long (570 m in total, and in the cost), but Eq. (2.24) uses L = 90 m in the 3 February example. |
| Tables 4.2–4.6 | Q_bi (heat to the evaporator) uses the October ratio q_b/q_y = 148/172 = 0.8605 in every month. Table 4.1 (November) uses 146/172. With the monthly enthalpies the ratio runs from 0.80 (January) to 0.86 (October). The model uses the monthly ratio; this changes only Q_bi, not the condenser heat or the compressor work. |
| Section 3.4 table | "Σ Total heat supplied = 10820 kW" should read kWh. |
| Table 3.11 | 1¼" PESCH-40 horizontal resistance "1.130" is very likely 0.130. |
| Appendix 1 | The rows for 1, 2 and 25 October 2013 differ from the temperatures the calculations used (see `data/README.md`). |
| Figure 3.10 | In 135 hours around 07:00 and 17:00 the tilt factor differs from Eq. (2.4) (see `docs/methodology.md`). |
