"""
Hoofdscript: extraheert data uit IFC en Excel naar CSV's,
en converteert ze vervolgens naar woningwaardering JSON.

Gebruik:
    .venv/Scripts/python.exe -m pipeline.run_pipeline [stap]

Stappen:
    extract   - Extraheert Excel en IFC naar CSV's
    json      - Converteert CSV's naar JSON (na handmatig invullen)
    all       - Beide stappen (default)
"""

import sys
from pipeline.config import (
    EXCEL_PATH,
    IFC_B2_PATH,
    IFC_B3_PATH,
    EENHEDEN_CSV,
    RUIMTEN_CSV,
    MAPPING_CSV,
    JSON_DIR,
)
from pipeline.extract_excel import extract_eenheden
from pipeline.extract_ifc import extract_rooms_from_ifc, write_ruimten_csv
from pipeline.link_eenheden import link_ruimten_to_eenheden
from pipeline.csv_to_json import convert_to_json


def run_extract():
    """Stap 1: Extraheer data naar CSV's."""
    print("=" * 60)
    print("STAP 1: Extractie naar CSV")
    print("=" * 60)

    # Excel -> eenheden.csv
    print("\n--- Excel extractie ---")
    extract_eenheden(EXCEL_PATH, EENHEDEN_CSV)

    # IFC -> ruimten.csv
    print("\n--- IFC extractie ---")
    apartments_b3 = extract_rooms_from_ifc(IFC_B3_PATH, "B3")
    apartments_b2 = extract_rooms_from_ifc(IFC_B2_PATH, "B2")
    all_apartments = apartments_b3 + apartments_b2
    write_ruimten_csv(all_apartments, RUIMTEN_CSV)

    # Koppel ruimten aan eenheden
    print("\n--- Koppeling ruimten <-> eenheden ---")
    link_ruimten_to_eenheden(EENHEDEN_CSV, RUIMTEN_CSV, MAPPING_CSV)

    # Samenvatting
    total_rooms = sum(len(a["rooms"]) for a in all_apartments)
    print(f"\n--- Samenvatting ---")
    print(f"  B3: {len(apartments_b3)} appartementen")
    print(f"  B2: {len(apartments_b2)} appartementen")
    print(f"  Totaal ruimten: {total_rooms}")
    print(f"\nOutput:")
    print(f"  {EENHEDEN_CSV}")
    print(f"  {RUIMTEN_CSV}")
    print(f"  {MAPPING_CSV}")
    print(f"\n>>> Vul nu de lege kolommen in de CSV's handmatig aan:")
    print(f"    - eenheden.csv: bouwjaar, klimaatbeheersing, WOZ, energielabel, monument")
    print(f"    - ruimten.csv: sanitair, aanrecht_lengte_mm")
    print(f"    Daarna: python -m pipeline.run_pipeline json")


def run_json():
    """Stap 2: Converteer CSV's naar JSON."""
    print("=" * 60)
    print("STAP 2: CSV -> JSON conversie")
    print("=" * 60)

    if not EENHEDEN_CSV.exists():
        print(f"FOUT: {EENHEDEN_CSV} niet gevonden. Draai eerst: python -m pipeline.run_pipeline extract")
        return
    if not RUIMTEN_CSV.exists():
        print(f"FOUT: {RUIMTEN_CSV} niet gevonden. Draai eerst: python -m pipeline.run_pipeline extract")
        return

    count = convert_to_json(EENHEDEN_CSV, RUIMTEN_CSV, JSON_DIR)
    print(f"\nJSON bestanden staan in: {JSON_DIR}")


def main():
    step = sys.argv[1] if len(sys.argv) > 1 else "all"

    if step == "extract":
        run_extract()
    elif step == "json":
        run_json()
    elif step == "all":
        run_extract()
        print("\n")
        run_json()
    else:
        print(f"Onbekende stap: {step}")
        print("Gebruik: python -m pipeline.run_pipeline [extract|json|all]")
        sys.exit(1)


if __name__ == "__main__":
    main()
