"""Converteert de eenheden.csv en ruimten.csv naar woningwaardering JSON-bestanden."""

import csv
import json
from pathlib import Path


def _read_csv(path: Path) -> list[dict]:
    """Leest een CSV-bestand met puntkomma-scheiding."""
    with open(path, "r", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter=";"))


def _make_ref(code: str, naam: str) -> dict:
    """Maakt een Referentiedata object."""
    return {"code": code, "naam": naam}


def _build_ruimte(row: dict) -> dict:
    """Bouwt een EenhedenRuimte JSON-object uit een ruimten.csv rij."""
    ruimte = {
        "id": row["ruimte_id"],
        "naam": row["naam"],
        "soort": _make_ref(row["soort_code"], row["soort_naam"]),
        "detailSoort": _make_ref(row["detail_soort_code"], row["detail_soort_naam"]),
        "oppervlakte": float(row["oppervlakte_m2"]) if row["oppervlakte_m2"] else 0,
        "verwarmd": row["verwarmd"].lower() == "ja",
    }

    # Optionele velden
    if row.get("inhoud_m3"):
        ruimte["inhoud"] = float(row["inhoud_m3"])
    if row.get("hoogte_mm"):
        hoogte = float(row["hoogte_mm"])
        if hoogte > 0:
            ruimte["hoogte"] = round(hoogte / 1000, 2)  # mm -> m
    if row.get("verkoeld", "").lower() == "ja":
        ruimte["verkoeld"] = True
    if row.get("afsluitbaar"):
        ruimte["afsluitbaar"] = row["afsluitbaar"].lower() == "ja"
    if row.get("bouwlaag"):
        ruimte["bouwlaag"] = {"nummer": row["bouwlaag"]}
    if row.get("gedeeld_met_aantal"):
        ruimte["gedeeldMetAantalEenheden"] = int(row["gedeeld_met_aantal"])

    # Bouwkundige elementen en installaties
    bouwkundige_elementen = []
    installaties = []

    # Sanitair — alle sanitaire voorzieningen als installaties
    if row.get("sanitair"):
        sanitair_items = [s.strip() for s in row["sanitair"].split(",") if s.strip()]
        installatie_map = {
            "DOU": "Douche",
            "BAD": "Bad",
            "WAS": "Wastafel",
            "CLO": "Toilet",
            "STO": "Staand toilet",
        }
        for code in sanitair_items:
            code_upper = code.upper()
            if code_upper in installatie_map:
                installaties.append(_make_ref(code_upper, installatie_map[code_upper]))

    # Aanrecht
    if row.get("aanrecht_lengte_mm"):
        try:
            lengte = int(row["aanrecht_lengte_mm"])
            bouwkundige_elementen.append({
                "id": f"{row['ruimte_id']}_AAN",
                "naam": "Aanrecht",
                "soort": _make_ref("KEU", "Keuken voorziening"),
                "detailSoort": _make_ref("AAN", "Aanrecht"),
                "lengte": lengte,
            })
        except ValueError:
            pass

    if bouwkundige_elementen:
        ruimte["bouwkundigeElementen"] = bouwkundige_elementen
    if installaties:
        ruimte["installaties"] = installaties

    return ruimte


def convert_to_json(
    eenheden_csv: Path,
    ruimten_csv: Path,
    output_dir: Path,
):
    """
    Leest de CSV's en genereert een JSON-bestand per eenheid.

    Alleen eenheden met gekoppelde ruimten worden geconverteerd.
    """
    eenheden = _read_csv(eenheden_csv)
    ruimten = _read_csv(ruimten_csv)

    # Groepeer ruimten per eenheid_id
    ruimten_per_eenheid = {}
    for row in ruimten:
        eid = row.get("eenheid_id", "").strip()
        if eid:
            ruimten_per_eenheid.setdefault(eid, []).append(row)

    output_dir.mkdir(parents=True, exist_ok=True)
    generated = 0
    skipped = 0

    for eenheid in eenheden:
        eid = str(eenheid["eenheid_id"]).strip()
        rooms = ruimten_per_eenheid.get(eid, [])

        if not rooms:
            skipped += 1
            continue

        # Bouw EenhedenEenheid JSON
        result = {
            "id": eid,
            "woningwaarderingstelsel": _make_ref(
                eenheid.get("woningwaarderingstelsel", "ZEL"),
                "Zelfstandige woonruimte"
                if eenheid.get("woningwaarderingstelsel") == "ZEL"
                else "Onzelfstandige woonruimten",
            ),
            "ruimten": [_build_ruimte(r) for r in rooms],
        }

        # Optionele eenheid-velden
        if eenheid.get("bouwjaar"):
            result["bouwjaar"] = int(eenheid["bouwjaar"])

        # Adres
        adres = {}
        if eenheid.get("straat"):
            adres["straatnaam"] = eenheid["straat"]
        if eenheid.get("huisnummer"):
            adres["huisnummer"] = str(eenheid["huisnummer"])
        if eenheid.get("huisletter"):
            adres["huisnummerToevoeging"] = eenheid["huisletter"]
        if eenheid.get("postcode"):
            adres["postcode"] = eenheid["postcode"]
        if eenheid.get("plaats"):
            adres["woonplaats"] = {"naam": eenheid["plaats"]}
        if adres:
            result["adres"] = adres

        # BAG
        if eenheid.get("bag_verblijfsobject"):
            result["adresseerbaarObjectBasisregistratie"] = {
                "id": str(eenheid["bag_verblijfsobject"]),
                "bagIdentificatie": str(eenheid["bag_verblijfsobject"]),
            }

        # Pandsoort
        if eenheid.get("pandsoort"):
            pandsoort_naam = (
                "Eengezinswoning" if eenheid["pandsoort"] == "EGW" else "Meergezinswoning"
            )
            result["panden"] = [
                {"soort": _make_ref(eenheid["pandsoort"], pandsoort_naam)}
            ]

        # Klimaatbeheersing
        if eenheid.get("klimaatbeheersing"):
            klim_naam = (
                "Individueel" if eenheid["klimaatbeheersing"] == "IND" else "Gemeenschappelijk"
            )
            result["klimaatbeheersing"] = [
                _make_ref(eenheid["klimaatbeheersing"], klim_naam)
            ]

        # WOZ
        if eenheid.get("woz_waarde"):
            woz = {"vastgesteldeWaarde": float(eenheid["woz_waarde"])}
            if eenheid.get("woz_peildatum"):
                woz["waardepeildatum"] = eenheid["woz_peildatum"]
            result["wozEenheden"] = [woz]

        # Energieprestatie
        if eenheid.get("energielabel"):
            ep = {
                "label": _make_ref(eenheid["energielabel"], eenheid["energielabel"]),
            }
            if eenheid.get("energieprestatie_soort"):
                soort_naam_map = {
                    "NTA": "Energielabel conform NTA8800",
                    "EI": "Energie-index",
                }
                ep["soort"] = _make_ref(
                    eenheid["energieprestatie_soort"],
                    soort_naam_map.get(eenheid["energieprestatie_soort"], ""),
                )
            if eenheid.get("energieprestatie_waarde"):
                ep["waarde"] = eenheid["energieprestatie_waarde"]
            if eenheid.get("energieprestatie_begindatum"):
                ep["begindatum"] = eenheid["energieprestatie_begindatum"]
            if eenheid.get("energieprestatie_einddatum"):
                ep["einddatum"] = eenheid["energieprestatie_einddatum"]
            ep["status"] = _make_ref("DEF", "Definitief")
            result["energieprestaties"] = [ep]

        # Monument
        result["monumenten"] = []
        if eenheid.get("monument"):
            mon_naam_map = {
                "RM": "Rijksmonument",
                "GM": "Gemeentelijk monument",
                "PM": "Provinciaal monument",
                "BSG": "Beschermd stadsgezicht",
            }
            result["monumenten"] = [
                _make_ref(
                    eenheid["monument"],
                    mon_naam_map.get(eenheid["monument"], eenheid["monument"]),
                )
            ]

        # Gebruiksoppervlakte
        if eenheid.get("gebruiksoppervlakte"):
            result["gebruiksoppervlakte"] = int(float(eenheid["gebruiksoppervlakte"]))

        # Schrijf JSON
        json_path = output_dir / f"{eid}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        generated += 1

    print(f"\nJSON generatie: {generated} bestanden geschreven, {skipped} overgeslagen (geen ruimten)")
    return generated
