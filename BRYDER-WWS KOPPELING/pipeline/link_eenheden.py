"""Koppelt ruimten aan eenheden op basis van type-matching (hoek↔hoek, std↔std)."""

import csv
from pathlib import Path


def _read_csv(path: Path) -> list[dict]:
    with open(path, "r", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter=";"))


def link_ruimten_to_eenheden(eenheden_csv: Path, ruimten_csv: Path, mapping_csv: Path):
    """
    Koppelt IFC-appartementen aan eenheden uit het Excel-bestand.

    Strategie: binnen elk gebouw (B2/B3) worden hoek-appartementen
    sequentieel gematcht op hoek-eenheden, en std op std.

    Schrijft mapping.csv en werkt ruimten.csv bij met eenheid_id en bouwnummer.
    """
    eenheden = _read_csv(eenheden_csv)
    ruimten = _read_csv(ruimten_csv)

    # Unieke appartementen uit ruimten
    apts = {}
    for row in ruimten:
        key = (row["building"], row["apt_type"], int(row["apt_index"]))
        if key not in apts:
            apts[key] = {"total_area": 0, "rooms": 0}
        apts[key]["total_area"] += float(row["oppervlakte_m2"]) if row["oppervlakte_m2"] else 0
        apts[key]["rooms"] += 1

    # Splits eenheden per building en type
    eenheden_split = {}
    for row in eenheden:
        t = row["type_overzicht"]
        if not (t.startswith("B2") or t.startswith("B3")):
            continue
        bld = "B3" if t.startswith("B3") else "B2"
        typ = "hoek" if "hoek" in t else "std"
        eenheden_split.setdefault((bld, typ), []).append(row)

    # Match: hoek↔hoek, std↔std per building
    mapping = {}
    for building in ["B3", "B2"]:
        for typ in ["hoek", "std"]:
            ifc_keys = sorted(
                [k for k in apts if k[0] == building and k[1] == typ],
                key=lambda x: x[2],
            )
            excel_rows = eenheden_split.get((building, typ), [])
            for ifc_key, eenheid in zip(ifc_keys, excel_rows):
                mapping[ifc_key] = {
                    "eid": eenheid["eenheid_id"],
                    "bn": int(eenheid["bouwnummer"]),
                    "hn": eenheid["huisnummer"],
                }

    # Schrijf mapping.csv
    mapping_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(mapping_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([
            "building", "apt_type", "apt_index", "rooms", "area_m2",
            "eenheid_id", "bouwnummer", "huisnummer",
        ])
        for key in sorted(mapping.keys(), key=lambda k: mapping[k]["bn"]):
            v = apts[key]
            e = mapping[key]
            writer.writerow([
                key[0], key[1], key[2], v["rooms"],
                round(v["total_area"], 1), e["eid"], e["bn"], e["hn"],
            ])

    # Update ruimten.csv
    for row in ruimten:
        key = (row["building"], row["apt_type"], int(row["apt_index"]))
        if key in mapping:
            row["eenheid_id"] = mapping[key]["eid"]
            row["bouwnummer"] = mapping[key]["bn"]

    fieldnames = list(ruimten[0].keys())
    with open(ruimten_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(ruimten)

    print(f"Mapping geschreven: {mapping_csv} ({len(mapping)} koppelingen)")
    print(f"Ruimten CSV bijgewerkt met eenheid_id en bouwnummer")
    return len(mapping)
