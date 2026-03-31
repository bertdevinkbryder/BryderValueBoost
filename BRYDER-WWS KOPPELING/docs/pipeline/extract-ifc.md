# extract_ifc.py -- IFC-extractie

Extraheert ruimten uit IFC-bestanden (BIM-modellen) en groepeert ze in appartementen.

## Functies

### `extract_rooms_from_ifc(ifc_path, building_code)`

Opent een IFC-bestand, extraheert alle `IfcSpace`-entiteiten, filtert gemeenschappelijke en meta-ruimten, en groepeert de overblijvende ruimten in appartementen.

**Returns:** lijst van apartment-dicts met type, index en rooms (inclusief quantities en VERA-codes).

### `write_ruimten_csv(all_apartments, output_path)`

Schrijft alle ruimten naar een semicolon-gescheiden CSV met UTF-8 BOM.

## Verwerkingsstappen

### 1. Laden en filteren

Alle `IfcSpace`-entiteiten worden geladen. Uitgefilterd worden:
- Ruimten met `LongName` in `COMMON_SPACES` of met "fietsenstalling"
- Entries met `:` in de `Name` (area/GO/VG/VR-entries)
- Entries die beginnen met "vg ", "vr ", "go ", "bc"

### 2. Sorteren

Ruimten worden gesorteerd op het numerieke deel van hun `Name`. Voorbeeld: `0.07.2791` -> sorteert op `2791`. Dit zorgt ervoor dat ruimten van hetzelfde appartement aaneengesloten staan.

### 3. Appartement-groepering

De IFC-modellen bevatten geen expliciete appartement-hiërarchie. Ruimten worden gegroepeerd op basis van sequentiële patronen:

#### Standaard appartement (8 kamers)

Herkend wanneer een blok begint met "slaapkamer 2" en positie 5 is "berging/techniek":

```
slaapkamer 2
slaapkamer 1
hal
MK warm
MK koud
berging / techniek
woonkamer / keuken
badkamer / toilet
```

#### Hoek appartement (6 kamers)

Herkend wanneer een blok begint met "woonkamer / keuken" en "entree" in het blok zit:

```
woonkamer / keuken
slaapkamer 1 / slaapkamer 2
slaapkamer 2 / slaapkamer 1
entree
badkamer
technische ruimte
```

#### Fallback-groepering

Als geen van de standaardpatronen matcht, worden opeenvolgende hoek-type kamers verzameld. Een groep van 5+ kamers met "entree" of "technische ruimte" wordt als hoek-appartement herkend. Meterkasten die tussenin staan worden apart verzameld.

#### Post-processing: hoek-reparatie

Na de initiële groepering worden hoek-appartementen gevalideerd. Appartementen met een afwijkend aantal woonkamers (0 of 2+) zijn foutief gegroepeerd -- dit treedt op in het B2-model waar kamers van verschillende appartementen door elkaar staan (IFC IDs 156-183).

De reparatiestap (`_fix_hoek_grouping`):
1. Detecteert hoek-appartementen met != 1 woonkamer
2. Verzamelt alle kamers uit foutieve groepen in een pool
3. Hergroepeert per woonkamer, met matching op afmetingen:
   - **Type A** (links): woonkamer ~28.04 m², slaapkamer 1 ~10.81 m², entree ~10.58 m²
   - **Type B** (rechts): woonkamer ~27.88 m², slaapkamer 1 ~11.18 m², entree ~10.36 m²
4. Wijst de best passende kamer van elk type toe aan elk appartement

### 4. Quantities uitlezen

Per ruimte worden `BaseQuantities` uit `IfcElementQuantity` gehaald:

| Quantity | Type | Gebruik |
|----------|------|---------|
| `NetFloorArea` | IfcQuantityArea | Oppervlakte in m2 |
| `GrossVolume` | IfcQuantityVolume | Inhoud in m3 |
| `Height` | IfcQuantityLength | Hoogte in mm |

### 5. VERA-mapping

Elke ruimte wordt via `ROOM_TYPE_MAP` gemapt naar VERA-codes. Zie [config.md](config.md) voor de volledige mapping.

## Output: ruimten.csv

22 kolommen:

| Kolom | Bron | Beschrijving |
|-------|------|-------------|
| `eenheid_id` | Automatisch (link_eenheden) | Koppeling naar eenheden.csv |
| `bouwnummer` | Automatisch (link_eenheden) | Bouwnummer van de woning |
| `building` | IFC | B2 of B3 |
| `apt_type` | Afgeleid | std of hoek |
| `apt_index` | Afgeleid | Volgnummer appartement |
| `ruimte_id` | IFC (Name) | IFC space naam (bijv. 0.07.2791) |
| `ifc_guid` | IFC (GlobalId) | Unieke IFC identifier |
| `naam` | IFC (LongName) | Ruimtenaam (bijv. "Woonkamer / keuken") |
| `soort_code` | Mapping | VTK, VRK, OVR of BTR |
| `soort_naam` | Mapping | Vertrek, Verkeersruimte, etc. |
| `detail_soort_code` | Mapping | WOO, SLA, BAD, HAL, etc. |
| `detail_soort_naam` | Mapping | Woonkamer, Slaapkamer, etc. |
| `oppervlakte_m2` | IFC | NetFloorArea |
| `inhoud_m3` | IFC | GrossVolume |
| `hoogte_mm` | IFC | Height |
| `verwarmd` | Mapping | ja of nee |
| `verkoeld` | Vast: nee | Altijd nee |
| `afsluitbaar` | **Handmatig** | ja of nee |
| `bouwlaag` | **Handmatig** | Verdiepingsnummer |
| `sanitair` | **Handmatig** | Codes: DOU,WAS,CLO etc. |
| `aanrecht_lengte_mm` | **Handmatig** | Lengte in mm |
| `gedeeld_met_aantal` | **Handmatig** | Aantal delende eenheden |

## Resultaten

| Building | Hoek | Standaard | Totaal appartementen | Ruimten |
|----------|------|-----------|---------------------|---------|
| B3 | 8 | 25 | 33 | 248 |
| B2 | 8 | 25 | 33 | 247 |
| **Totaal** | **16** | **50** | **66** | **495** |

**Bekende beperkingen:**
- B2 hoek-appartement idx=32 heeft 5 kamers (technische ruimte ontbreekt, room 184 was orphaned in het IFC-model)
- B1-woningen (95 stuks) hebben geen IFC-data
