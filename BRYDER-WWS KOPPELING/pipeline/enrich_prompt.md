# CSV Enrichment Instructions

Follow these instructions to fill in missing values in `output/eenheden.csv` and `output/ruimten.csv` with reasonable defaults for the Fascinatio nieuwbouw project.

## Project Context

- **Project**: Nieuwebouwen Fascinatio, Capelle aan den IJssel (Havensteder)
- **Type**: New construction, expected completion ~2025
- **Buildings B2 and B3**: Apartment blocks, 33 units each (66 total with IFC room data)
- **Building B1**: 95 eengezinswoningen — no IFC data, no linked rooms in ruimten.csv
- **Stelsel**: Zelfstandige woonruimten (self-contained units)

## CSV Format

- Delimiter: semicolon (`;`)
- Encoding: `utf-8-sig` (BOM)
- When writing back, preserve column order and encoding exactly

## Rules: Only Fill Empty Cells

**Critical**: never overwrite a cell that already has a value. Only fill cells that are empty or blank. This makes the process idempotent and safe to re-run after manual edits.

---

## Step 1: Enrich `output/ruimten.csv`

Read the file. For each row, apply these rules to empty cells:

### sanitair

Look at `detail_soort_code` and `naam`:

| Condition | Value |
|-----------|-------|
| `detail_soort_code` is `BAD` AND `naam` contains "toilet" (case-insensitive) | `DOU,WAS,CLO` |
| `detail_soort_code` is `BAD` AND `naam` does NOT contain "toilet" | `DOU,WAS` |
| Any other room type | Leave empty |

Reasoning: Bathrooms with toilet get shower + washbasin + toilet. Bathrooms without toilet get shower + washbasin. Other rooms have no sanitary facilities.

### aanrecht_lengte_mm

| Condition | Value |
|-----------|-------|
| `detail_soort_code` is `WOO` AND `naam` contains "keuken" (case-insensitive) | `2100` |
| Any other room type | Leave empty |

Reasoning: Standard kitchen countertop length is 2100mm (2.1m). Only woonkamer/keuken combination rooms have a kitchen counter.

### afsluitbaar

| Condition | Value |
|-----------|-------|
| `soort_code` is `VTK` (vertrekken: woonkamer, slaapkamer, badkamer) | `ja` |
| `soort_code` is `VRK` or `OVR` (verkeersruimten, overige) | `nee` |

Reasoning: Living spaces (vertrekken) are closable rooms. Circulation and utility spaces generally are not.

### bouwlaag

Leave empty — not used in the WWS calculation.

### gedeeld_met_aantal

Leave empty — these are self-contained apartments with no shared rooms.

Write the updated ruimten.csv back.

---

## Step 2: Enrich `output/eenheden.csv`

First, read `pipeline/config.py` to get the current `WOZ_EUR_PER_M2` value.

Then read `output/eenheden.csv`. For each row, apply these rules to empty cells:

### Fixed defaults

| Field | Value | Reasoning |
|-------|-------|-----------|
| `bouwjaar` | `2025` | New construction project |
| `klimaatbeheersing` | `IND` | Modern new builds have individual (individueel) heating/cooling |
| `energielabel` | `A` | Dutch new construction must meet BENG requirements, typically label A or better |
| `energieprestatie_soort` | `NTA` | NTA8800 is the current energy performance standard |
| `energieprestatie_waarde` | `0.4` | Reasonable numeric value for a label A new-build apartment |
| `energieprestatie_begindatum` | `2025-01-01` | Estimated start date of energy certificate |
| `energieprestatie_einddatum` | `2035-01-01` | 10-year validity period |
| `woz_peildatum` | `2024-01-01` | WOZ valuation always uses January 1 of the prior year |
| `monument` | _(leave empty)_ | New construction is never a monument |

### Calculated: gebruiksoppervlakte

For each `eenheid_id` that has linked rooms in ruimten.csv:
1. Filter ruimten.csv rows matching that `eenheid_id`
2. Keep only rows where `soort_code` is `VTK` or `VRK` (vertrekken + verkeersruimten)
3. Sum their `oppervlakte_m2` values
4. Round to nearest integer
5. Fill the `gebruiksoppervlakte` cell

This follows the NEN 2580 definition of gebruiksoppervlakte. Units without linked rooms (B1 eenheden) will remain empty.

### Calculated: woz_waarde

For each row where `gebruiksoppervlakte` is filled (either just now or previously):
1. Calculate: `round(float(gebruiksoppervlakte) * WOZ_EUR_PER_M2)`
2. Fill the `woz_waarde` cell

The `WOZ_EUR_PER_M2` value comes from `pipeline/config.py`. This is an estimate — flag it in the summary.

Write the updated eenheden.csv back.

---

## Step 3: Run Woningwaardering Calculator

After enriching and regenerating the JSON files (`python -m pipeline json`), run the woningwaardering calculator on each JSON and write the results back into `output/eenheden.csv`.

### How to call the calculator

```python
import sys
sys.path.insert(0, "woningwaardering")

from datetime import date
from woningwaardering import Woningwaardering
from woningwaardering.vera.bvg.generated import EenhedenEenheid

wws = Woningwaardering(peildatum=date(2026, 1, 1))

with open(f"output/json/{eenheid_id}.json", "r") as f:
    eenheid = EenhedenEenheid.model_validate_json(f.read())

resultaat = wws.waardeer(eenheid)
```

### Result fields to extract

From the `resultaat` object, extract these top-level values:

| CSV Column | Source | Description |
|------------|--------|-------------|
| `wws_punten` | `resultaat.punten` | Total WWS points |
| `wws_maximale_huur` | `resultaat.maximale_huur` | Maximum rent in EUR |

And extract points per stelselgroep from `resultaat.groepen`:

| CSV Column | Stelselgroep Code | Description |
|------------|-------------------|-------------|
| `wws_oppervlakte_vertrekken` | OVZ | Oppervlakte van vertrekken |
| `wws_oppervlakte_overige` | OOZ | Oppervlakte van overige ruimten |
| `wws_verkoeling_verwarming` | VKV | Verkoeling en verwarming |
| `wws_buitenruimten` | BUI | Buitenruimten |
| `wws_energieprestatie` | ENE | Energieprestatie |
| `wws_keuken` | KEU | Keuken |
| `wws_sanitair` | SAN | Sanitair |
| `wws_gemeenschappelijk_parkeren` | GPA | Gemeenschappelijke parkeerruimten |
| `wws_gemeenschappelijk_vertrekken` | GVR | Gemeenschappelijke vertrekken etc. |
| `wws_woz_waarde` | WOZ | Punten voor de WOZ-waarde |
| `wws_bijzondere_voorzieningen` | BIJ | Bijzondere voorzieningen |
| `wws_prijsopslag_monumenten` | PMN | Prijsopslag monumenten en nieuwbouw |

### How to extract group points

```python
for groep in resultaat.groepen:
    code = groep.criterium_groep.stelselgroep.code
    punten = groep.punten
    # Map code to CSV column name and store
```

### Writing results

- Add all `wws_*` columns to `output/eenheden.csv`
- Only fill rows where a JSON file exists (66 B2/B3 units)
- B1 units (95 rows) will have empty wws columns
- If a `wws_punten` column already has a value for a row, skip it (idempotent)

### Error handling

If the calculator fails for a specific unit, log the error and continue with the next unit. Don't abort the whole run.

---

## Step 4: Print Summary

After all steps are complete, print a summary showing:
- How many rows were updated per field in ruimten.csv
- How many rows were updated per field in eenheden.csv
- How many units were scored by the woningwaardering calculator
- For scored units: min/max/avg total points and maximale huur
- Warning: X B1 units could not be scored (no JSON files)
- Warning: woz_waarde is estimated at EUR X/m2 — verify before final calculation

---

## Implementation Approach

Use a Python script via Bash to do the actual CSV manipulation and calculator run. Write a Python script that:
1. Reads both CSVs with pandas (`sep=";"`, `encoding="utf-8-sig"`, `dtype=str`)
2. Applies all enrichment rules above (only filling empty/NaN cells)
3. Writes back enriched CSVs
4. Runs `python -m pipeline json` to regenerate JSON files
5. Loads each JSON, runs the woningwaardering calculator, extracts results
6. Adds wws_* columns to eenheden.csv and writes back
7. Prints the full summary
