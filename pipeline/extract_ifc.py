"""Extraheert ruimten uit IFC-bestanden en groepeert ze in appartementen."""

import csv
import ifcopenshell
from pathlib import Path
from pipeline.config import ROOM_TYPE_MAP, COMMON_SPACES


def _num_key(name: str) -> int:
    """Haalt het numerieke deel uit een IFC space-naam (bijv. '0.07.2791' -> 2791)."""
    if ":" in name:
        return 999999
    parts = name.split(".")
    try:
        return int(parts[-1])
    except (ValueError, IndexError):
        return 999999


def _is_common_or_meta(longname: str, name: str) -> bool:
    """Bepaalt of een ruimte een gemeenschappelijke of meta-ruimte is."""
    ln = longname.lower()
    if ln in COMMON_SPACES or "fietsenstalling" in ln:
        return True
    # Area/GO/VG/VR/BC entries zijn geen echte ruimten
    if ":" in name:
        return True
    if any(ln.startswith(p) for p in ("vg ", "vr ", "go ", "bc")):
        return True
    return False


def _get_base_quantities(space):
    """Haalt BaseQuantities op voor een IfcSpace."""
    quantities = {}
    for rel in space.IsDefinedBy:
        if rel.is_a("IfcRelDefinesByProperties"):
            pset = rel.RelatingPropertyDefinition
            if pset.is_a("IfcElementQuantity") and pset.Name == "BaseQuantities":
                for q in pset.Quantities:
                    if q.is_a("IfcQuantityArea"):
                        quantities[q.Name] = q.AreaValue
                    elif q.is_a("IfcQuantityVolume"):
                        quantities[q.Name] = q.VolumeValue
                    elif q.is_a("IfcQuantityLength"):
                        quantities[q.Name] = q.LengthValue
    return quantities


def _get_storey(space, ifc_file):
    """Bepaalt de verdieping van een IfcSpace."""
    for rel in ifc_file.by_type("IfcRelContainedInSpatialStructure"):
        if space in rel.RelatedElements:
            struct = rel.RelatingStructure
            if struct.is_a("IfcBuildingStorey"):
                return struct.Name or ""
    return ""


def _group_apartments(sorted_rooms):
    """
    Groepeert ruimten in appartementen op basis van sequentiële ID-patronen.

    Standaard appartement (8 kamers):
        slaapkamer 2, slaapkamer 1, hal, MK warm, MK koud,
        berging/techniek, woonkamer / keuken, badkamer/toilet

    Hoek appartement (6 kamers):
        woonkamer / keuken, slaapkamer ?, slaapkamer ?,
        entree, badkamer, technische ruimte
    """
    apartments = []
    meterkast_pool = []  # Losse meterkasten voor hoek-appartementen
    idx = 0
    rooms = sorted_rooms

    while idx < len(rooms):
        space, num, longname = rooms[idx]
        ln = longname.lower()

        # Meterkast apart verzamelen
        if "meterkast" in ln:
            meterkast_pool.append(rooms[idx])
            idx += 1
            continue

        # Standaard appartement: begint met slaapkamer 2, 8 kamers
        if ln == "slaapkamer 2" and idx + 7 < len(rooms):
            block = rooms[idx : idx + 8]
            block_names = [r[2].lower() for r in block]
            if block_names[5] == "berging/techniek":
                apartments.append(
                    {"type": "std", "rooms": [r[0] for r in block]}
                )
                idx += 8
                continue

        # Hoek appartement: begint met woonkamer / keuken, 6 kamers
        if ln == "woonkamer / keuken" and idx + 5 < len(rooms):
            block = rooms[idx : idx + 6]
            block_names = [r[2].lower() for r in block]
            # Controleer of er een entree in zit (typisch op positie 3)
            if "entree" in block_names:
                apartments.append(
                    {"type": "hoek", "rooms": [r[0] for r in block]}
                )
                idx += 6
                continue

        # Fallback: losse hoek-kamers verzamelen tot we er 5 of 6 hebben
        # Dit vangt rommelige B2-secties op
        hoek_types = {"woonkamer / keuken", "slaapkamer 1", "slaapkamer 2", "entree", "badkamer", "technische ruimte"}
        if ln in hoek_types:
            hoek_rooms = [rooms[idx]]
            lookahead = idx + 1
            while lookahead < len(rooms) and len(hoek_rooms) < 6:
                _, _, next_ln = rooms[lookahead]
                next_lower = next_ln.lower()
                if next_lower in hoek_types:
                    hoek_rooms.append(rooms[lookahead])
                    lookahead += 1
                elif "meterkast" in next_lower:
                    meterkast_pool.append(rooms[lookahead])
                    lookahead += 1
                else:
                    break

            names_in_group = {r[2].lower() for r in hoek_rooms}
            has_hoek_markers = "entree" in names_in_group or "technische ruimte" in names_in_group
            if len(hoek_rooms) >= 5 and has_hoek_markers:
                apartments.append(
                    {"type": "hoek", "rooms": [r[0] for r in hoek_rooms]}
                )
                idx = lookahead
                continue

        # Overslaan als we niets kunnen groeperen
        print(f"  [skip] {rooms[idx][1]:>5}: {longname}")
        idx += 1

    # Post-processing: repareer foutief gegroepeerde hoek-appartementen
    apartments = _fix_hoek_grouping(apartments)

    return apartments, meterkast_pool


def _fix_hoek_grouping(apartments):
    """
    Repareert hoek-appartementen die foutief gegroepeerd zijn.

    Detecteert appartementen met meerdere woonkamers (gemerged) of zonder
    woonkamer (orphan-rooms), verzamelt alle kamers in een pool, en hergroepeert
    ze op basis van kamertype en afmetingen.
    """
    good = []
    pool = []  # (space, longname_lower) tuples van foutieve groepen

    for apt in apartments:
        if apt["type"] != "hoek":
            good.append(apt)
            continue

        wk_count = sum(
            1 for s in apt["rooms"]
            if "woonkamer" in (s.LongName or "").lower()
        )
        if wk_count == 1:
            good.append(apt)
        else:
            # Foutief: pool alle kamers voor hergroepering
            for s in apt["rooms"]:
                pool.append(s)

    if not pool:
        return apartments

    print(f"  [fix] {len(pool)} kamers uit foutieve hoek-groepen hergroeperen")

    # Groepeer pool-kamers per type
    woonkamers = []
    slaapkamers_1 = []
    slaapkamers_2 = []
    entrees = []
    badkamers = []
    tech_ruimtes = []

    for s in pool:
        ln = (s.LongName or "").lower()
        if "woonkamer" in ln:
            woonkamers.append(s)
        elif ln == "slaapkamer 1":
            slaapkamers_1.append(s)
        elif ln == "slaapkamer 2":
            slaapkamers_2.append(s)
        elif ln == "entree":
            entrees.append(s)
        elif ln == "badkamer":
            badkamers.append(s)
        elif "technische ruimte" in ln:
            tech_ruimtes.append(s)

    # Hergroepeer: elke woonkamer start een nieuw appartement
    # Match op basis van afmetingen (Type A: entree ~10.58, Type B: ~10.36)
    new_apts = []
    used_s1 = set()
    used_s2 = set()
    used_ent = set()
    used_bad = set()
    used_tech = set()

    def _area(space):
        for rel in space.IsDefinedBy:
            if rel.is_a("IfcRelDefinesByProperties"):
                pset = rel.RelatingPropertyDefinition
                if pset.is_a("IfcElementQuantity") and pset.Name == "BaseQuantities":
                    for q in pset.Quantities:
                        if q.is_a("IfcQuantityArea") and q.Name == "NetFloorArea":
                            return q.AreaValue
        return 0

    def _pick_closest(candidates, target_area, used):
        best = None
        best_diff = float("inf")
        for s in candidates:
            if id(s) in used:
                continue
            diff = abs(_area(s) - target_area)
            if diff < best_diff:
                best = s
                best_diff = diff
        if best:
            used.add(id(best))
        return best

    for wk in woonkamers:
        wk_area = _area(wk)
        # Type A: wk ~28.04, slk1 ~10.81, entree ~10.58
        # Type B: wk ~27.88, slk1 ~11.18, entree ~10.36
        is_type_a = wk_area > 27.95

        target_s1 = 10.81 if is_type_a else 11.18
        target_ent = 10.58 if is_type_a else 10.36

        rooms = [wk]
        s1 = _pick_closest(slaapkamers_1, target_s1, used_s1)
        s2 = _pick_closest(slaapkamers_2, 6.21, used_s2)
        ent = _pick_closest(entrees, target_ent, used_ent)
        bad = _pick_closest(badkamers, 5.09, used_bad)
        tech = _pick_closest(tech_ruimtes, 4.13, used_tech)

        for r in [s1, s2, ent, bad, tech]:
            if r:
                rooms.append(r)

        new_apts.append({"type": "hoek", "rooms": rooms})
        count_str = f"{len(rooms)} kamers"
        total = sum(_area(r) for r in rooms)
        print(f"  [fix] hergroepeerd hoek-appartement: {count_str}, {total:.1f} m²")

    # Voeg goede en herstelde appartementen samen, sorteer op originele index
    result = good + new_apts
    return result


def extract_rooms_from_ifc(ifc_path: Path, building_code: str):
    """
    Extraheert alle appartement-ruimten uit een IFC-bestand.

    Returns:
        list[dict]: Lijst van appartementen, elk met type, rooms (met quantities)
    """
    print(f"\nOpenen: {ifc_path.name} ...")
    ifc = ifcopenshell.open(str(ifc_path))
    spaces = ifc.by_type("IfcSpace")

    # Filter en sorteer
    room_list = []
    for s in spaces:
        name = s.Name or ""
        longname = s.LongName or ""
        if _is_common_or_meta(longname, name):
            continue
        num = _num_key(name)
        if num == 999999:
            continue
        room_list.append((s, num, longname))

    room_list.sort(key=lambda r: r[1])
    print(f"  {len(room_list)} ruimten na filtering")

    # Groepeer in appartementen
    apartments, meterkast_pool = _group_apartments(room_list)

    hoek_count = sum(1 for a in apartments if a["type"] == "hoek")
    std_count = sum(1 for a in apartments if a["type"] == "std")
    print(f"  Gevonden: {hoek_count} hoek + {std_count} std = {hoek_count + std_count} appartementen")
    print(f"  Losse meterkasten: {len(meterkast_pool)}")

    # Verrijk met quantities
    result = []
    for apt_idx, apt in enumerate(apartments):
        apt_rooms = []
        for space in apt["rooms"]:
            quantities = _get_base_quantities(space)
            longname = space.LongName or ""
            ln_lower = longname.lower()

            # Map naar VERA codes
            mapping = ROOM_TYPE_MAP.get(ln_lower)
            if not mapping:
                # Probeer generiek te matchen
                for key, val in ROOM_TYPE_MAP.items():
                    if key in ln_lower:
                        mapping = val
                        break
            if not mapping:
                mapping = ("OVR", "Overige ruimtes", "OVR", "Overige ruimte", False)

            soort_code, soort_naam, detail_code, detail_naam, verwarmd = mapping

            apt_rooms.append({
                "ifc_id": space.Name or "",
                "ifc_guid": space.GlobalId,
                "naam": longname,
                "soort_code": soort_code,
                "soort_naam": soort_naam,
                "detail_soort_code": detail_code,
                "detail_soort_naam": detail_naam,
                "oppervlakte": round(quantities.get("NetFloorArea", 0), 2),
                "inhoud": round(quantities.get("GrossVolume", 0), 2),
                "hoogte_mm": round(quantities.get("Height", 0), 0),
                "verwarmd": verwarmd,
            })

        result.append({
            "building": building_code,
            "type": apt["type"],
            "index": apt_idx,
            "rooms": apt_rooms,
        })

    return result


def write_ruimten_csv(all_apartments: list[dict], output_path: Path):
    """Schrijft alle ruimten naar een CSV-bestand."""
    fieldnames = [
        "eenheid_id",
        "bouwnummer",
        "building",
        "apt_type",
        "apt_index",
        "ruimte_id",
        "ifc_guid",
        "naam",
        "soort_code",
        "soort_naam",
        "detail_soort_code",
        "detail_soort_naam",
        "oppervlakte_m2",
        "inhoud_m3",
        "hoogte_mm",
        "verwarmd",
        "verkoeld",
        "afsluitbaar",
        "bouwlaag",
        "sanitair",
        "aanrecht_lengte_mm",
        "gedeeld_met_aantal",
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()

        for apt in all_apartments:
            for room in apt["rooms"]:
                writer.writerow({
                    "eenheid_id": "",  # Wordt later gekoppeld
                    "bouwnummer": "",  # Wordt later gekoppeld
                    "building": apt["building"],
                    "apt_type": apt["type"],
                    "apt_index": apt["index"],
                    "ruimte_id": room["ifc_id"],
                    "ifc_guid": room["ifc_guid"],
                    "naam": room["naam"],
                    "soort_code": room["soort_code"],
                    "soort_naam": room["soort_naam"],
                    "detail_soort_code": room["detail_soort_code"],
                    "detail_soort_naam": room["detail_soort_naam"],
                    "oppervlakte_m2": room["oppervlakte"],
                    "inhoud_m3": room["inhoud"],
                    "hoogte_mm": room["hoogte_mm"],
                    "verwarmd": "ja" if room["verwarmd"] else "nee",
                    "verkoeld": "nee",
                    "afsluitbaar": "",
                    "bouwlaag": "",
                    "sanitair": "",
                    "aanrecht_lengte_mm": "",
                    "gedeeld_met_aantal": "",
                })

    print(f"\nRuimten CSV geschreven: {output_path}")
