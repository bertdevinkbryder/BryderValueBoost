# config.py -- Configuratie

Centrale configuratie voor paden, ruimtetype-mappings en constanten.

## Paden

| Constante | Beschrijving | Waarde |
|-----------|-------------|--------|
| `BASE_DIR` | Project root | Automatisch bepaald |
| `HUISDATA_DIR` | Brondata Fascinatio | `huisdata/havensteder/Nieuwebouwen_Fascination_laatsteblok/` |
| `EXCEL_PATH` | Eenheden Excel | `fascinatio nieuwbouw 20250218.xlsx` |
| `IFC_B2_PATH` | IFC blok B2 | `FAS_PLE_BWK-B2.ifc` (264 MB, Revit) |
| `IFC_B3_PATH` | IFC blok B3 | `FAS_PLE_BWK-B3.ifc` (81 MB, Revit) |
| `EENHEDEN_CSV` | Output eenheden | `output/eenheden.csv` |
| `RUIMTEN_CSV` | Output ruimten | `output/ruimten.csv` |
| `JSON_DIR` | Output JSON's | `output/json/` |

## ROOM_TYPE_MAP

Mapt IFC `LongName` (lowercase) naar VERA-codes. Elke entry is een tuple:

```
(ruimtesoort_code, ruimtesoort_naam, detailsoort_code, detailsoort_naam, verwarmd)
```

| IFC LongName | Soort | Detail | Verwarmd |
|-------------|-------|--------|----------|
| woonkamer / keuken | VTK (Vertrek) | WOO (Woonkamer) | ja |
| slaapkamer 1, slaapkamer 2 | VTK | SLA (Slaapkamer) | ja |
| badkamer / toilet, badkamer | VTK | BAD (Badruimte) | ja |
| hal | VRK (Verkeersruimte) | HAL (Hal) | ja |
| entree | VRK | HAL (Hal) | nee |
| berging / techniek | OVR (Overige) | BER (Berging) | nee |
| technische ruimte | OVR | TEC (Technische ruimte) | nee |
| mk warm, mk koud, meterkast warm/koud | OVR | MET (Meterruimte) | nee |
| cvz kast | OVR | TEC (Technische ruimte) | nee |

Varianten met en zonder spaties rond `/` zijn beide opgenomen (bijv. `badkamer / toilet` en `badkamer/toilet`).

Als een IFC-naam niet in de map staat, wordt er generiek gematcht (substring) en anders valt het terug op `OVR / Overige ruimte`.

## COMMON_SPACES

Set van ruimtenamen die uitgesloten worden van appartement-groepering. Dit zijn gemeenschappelijke ruimten op gebouwniveau:

- fietsenstalling
- hydrofoor + werkkast
- installatieruimte warmte/koude
- distributiestation / trafo

Daarnaast worden namen die `"fietsenstalling"` bevatten of beginnen met `"vg "`, `"vr "`, `"go "`, `"bc"` ook uitgesloten. Entries met een `:` in de naam (area/GO/VG/VR-entries) worden eveneens overgeslagen.
