# Bryder WWS Koppeling

Pipeline die gebouwdata (IFC-modellen, Excel-registraties) omzet naar invoer voor de woningwaardering calculator.

## CSV Enrichment

To fill in missing values in the output CSVs with reasonable defaults for the Fascinatio nieuwbouw project, follow the instructions in `pipeline/enrich_prompt.md`.

The WOZ-waarde multiplier (EUR/m2) is configurable in `pipeline/config.py` via the `WOZ_EUR_PER_M2` constant.

The enrichment prompt also runs the woningwaardering calculator on each unit and writes WWS scores (total points, maximale huur, points per stelselgroep) back into eenheden.csv as `wws_*` columns. These CSVs are used for training and testing.
