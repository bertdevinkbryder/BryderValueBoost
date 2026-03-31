# Bryder WWS Koppeling

Pipeline die gebouwdata (IFC-modellen, Excel-registraties) omzet naar invoer voor de [woningwaardering](https://github.com/woonstadrotterdam/woningwaardering) calculator (Woningwaarderingsstelsel / WWS), draait de berekening, en schrijft de resultaten terug naar CSV.

## Wat doet dit project?

Het doel is om voor elk appartement in het Fascinatio-project (Capelle aan den IJssel, Havensteder) een WWS-puntentelling te genereren. De brondata komt uit twee systemen:

- **Excel** -- eenheden-registratie met OGE-nummers, adressen, BAG-ids en bouwnummers
- **IFC** -- BIM-modellen (Revit) met ruimten inclusief oppervlaktes, volumes en hoogtes

De pipeline haalt automatisch alles eruit wat er te halen valt, verrijkt de data met standaardwaarden, draait de woningwaardering calculator, en schrijft de resultaten terug naar CSV.

## Workflow

```
  Excel             eenheden.csv        verrijking         JSON per         WWS score
  IFC B2     -->    ruimten.csv    -->  (agent of   -->    eenheid    -->   terug in
  IFC B3            mapping.csv         handmatig)         (66 best.)      eenheden.csv
     extract                        enrich/handmatig    json              score
```

### Stap 1: `python -m pipeline extract`

Draait drie sub-stappen:

1. **extract_excel.py** -- leest 161 woningen uit Excel, schrijft `output/eenheden.csv`
2. **extract_ifc.py** -- leest IFC-modellen B2 en B3, groepeert kamers in appartementen (8 hoek + 25 std per gebouw), schrijft `output/ruimten.csv`
3. **link_eenheden.py** -- koppelt de 66 IFC-appartementen automatisch aan de juiste eenheid via type-matching (hoek op hoek, std op std), schrijft `output/mapping.csv` en vult `eenheid_id`/`bouwnummer` in ruimten.csv

### Stap 2: Verrijking

De CSV's bevatten lege kolommen die aangevuld moeten worden (bouwjaar, energielabel, sanitair, etc.). Dit kan op twee manieren:

**Optie A: Agentic (via Claude Code)**
Zeg tegen Claude Code: *"follow the instructions in pipeline/enrich_prompt.md"*. De agent vult standaardwaarden in op basis van het projectcontext (nieuwbouw, Capelle a/d IJssel). Zie [enrich_prompt.md](pipeline/enrich_prompt.md) voor de volledige instructies en aannames.

**Optie B: Handmatig**
Open `output/eenheden.csv` en `output/ruimten.csv` in Excel en vul de lege kolommen in. Zie [Wat moet er nog ingevuld worden?](#wat-moet-er-nog-ingevuld-worden) hieronder.

### Stap 3: `python -m pipeline json`

Leest de verrijkte CSV's en genereert per eenheid een VERA-conform JSON-bestand in `output/json/`. Alleen eenheden met gekoppelde ruimten worden geconverteerd (= de 66 B2/B3 appartementen).

### Stap 4: WWS berekening

De woningwaardering calculator draait op de JSON-bestanden en schrijft de resultaten terug als `wws_*` kolommen in `output/eenheden.csv`. Dit wordt meegenomen in de agentic verrijking (stap 2, optie A) of kan handmatig gedraaid worden — zie [WWS berekening draaien](#wws-berekening-draaien) hieronder.

## Output

Alle gegenereerde bestanden staan in `output/`:

| Bestand | Inhoud |
|---------|--------|
| `eenheden.csv` | 161 woningen met adressen, BAG-ids, verrijkte velden, en WWS scores (`wws_*` kolommen) |
| `ruimten.csv` | 495 kamers met oppervlaktes, sanitair, aanrecht, afsluitbaar |
| `mapping.csv` | 66 koppelingen IFC-appartement <-> eenheid |
| `json/` | 66 VERA JSON-bestanden (input voor de calculator) |

### WWS resultaat-kolommen in eenheden.csv

| Kolom | Inhoud |
|-------|--------|
| `wws_punten` | Totaal WWS-punten |
| `wws_maximale_huur` | Maximale huurprijs in EUR |
| `wws_oppervlakte_vertrekken` | Punten oppervlakte vertrekken (OVZ) |
| `wws_oppervlakte_overige` | Punten oppervlakte overige ruimten (OOZ) |
| `wws_verkoeling_verwarming` | Punten verkoeling en verwarming (VKV) |
| `wws_buitenruimten` | Punten buitenruimten (BUI) |
| `wws_energieprestatie` | Punten energieprestatie (ENE) |
| `wws_keuken` | Punten keuken (KEU) |
| `wws_sanitair` | Punten sanitair (SAN) |
| `wws_gemeenschappelijk_parkeren` | Punten gemeenschappelijke parkeerruimten (GPA) |
| `wws_gemeenschappelijk_vertrekken` | Punten gemeenschappelijke vertrekken etc. (GVR) |
| `wws_woz_waarde` | Punten WOZ-waarde (WOZ) |
| `wws_bijzondere_voorzieningen` | Punten bijzondere voorzieningen (BIJ) |
| `wws_prijsopslag_monumenten` | Prijsopslag monumenten en nieuwbouw (PMN) |

## Wat is al gedaan?

| Wat | Status | Toelichting |
|-----|--------|-------------|
| Excel-extractie (eenheden) | Klaar | 161 woningen, adressen, BAG-ids |
| IFC-extractie B3 (ruimten) | Klaar | 33 appartementen, 248 kamers |
| IFC-extractie B2 (ruimten) | Klaar | 33 appartementen, 247 kamers |
| Koppeling ruimten - eenheden | Klaar | 66 koppelingen via type-matching, zie `output/mapping.csv` |
| Appartement-groepering | Klaar | Standaard (8 kamers) en hoek (6 kamers) herkend |
| Hoek-reparatie B2 | Klaar | Interleaved kamers in IFC zone 156-183 automatisch hergroepeerd |
| VERA ruimtetype-mapping | Klaar | IFC-namen gemapt naar VTK/VRK/OVR codes |
| CSV-naar-JSON conversie | Klaar | Sanitair als installaties, aanrecht als bouwkundig element |
| Agentic verrijking | Klaar | Claude Code prompt voor standaardwaarden (nieuwbouw) |
| WWS berekening | Klaar | 66 appartementen gescoord, resultaten in eenheden.csv |

## Wat moet er nog ingevuld worden?

De agentic verrijking (`pipeline/enrich_prompt.md`) vult de meeste velden automatisch in met standaardwaarden voor nieuwbouw. Hieronder staat wat er per kolom wordt ingevuld en wat eventueel handmatig gecontroleerd moet worden.

### eenheden.csv -- per woning (66 rijen voor B2/B3)

| Kolom | Automatisch ingevuld | Handmatig controleren |
|-------|---------------------|----------------------|
| `bouwjaar` | `2025` (nieuwbouw) | Exact jaar vergunning |
| `klimaatbeheersing` | `IND` (individueel) | Check installatiebestek |
| `woz_waarde` | Geschat op `gebruiksoppervlakte * EUR 3200/m2` | WOZ-beschikking of WOZ-waardeloket |
| `woz_peildatum` | `2024-01-01` | |
| `energielabel` | `A` (BENG-nieuwbouw) | EP-Online of energielabel-register |
| `energieprestatie_soort` | `NTA` (NTA8800) | |
| `energieprestatie_waarde` | `0.4` | Exacte waarde uit energielabel |
| `energieprestatie_begindatum` | `2025-01-01` | Exacte datum |
| `energieprestatie_einddatum` | `2035-01-01` | |
| `monument` | Leeg (nieuwbouw) | Altijd leeg voor nieuwbouw |
| `gebruiksoppervlakte` | Berekend uit VTK+VRK ruimten | NEN 2580 / plattegronden |

De WOZ-waarde multiplier (`WOZ_EUR_PER_M2`) is configureerbaar in `pipeline/config.py`.

### ruimten.csv -- per kamer (495 rijen)

| Kolom | Automatisch ingevuld | Toelichting |
|-------|---------------------|-------------|
| `sanitair` | Op basis van kamertype | BAD+toilet: `DOU,WAS,CLO`; BAD: `DOU,WAS` |
| `aanrecht_lengte_mm` | `2100` voor woonkamer/keuken | Standaard aanrechtlengte |
| `afsluitbaar` | `ja` voor VTK, `nee` voor VRK/OVR | |
| `bouwlaag` | Niet ingevuld | Niet nodig voor WWS-berekening |
| `gedeeld_met_aantal` | Niet ingevuld | Zelfstandige woningen |

### Nog niet gedekt: B1-woningen (95 stuks)

De 95 B1-woningen (eengezinswoningen, bouwnummer 67-161) staan wel in eenheden.csv maar hebben **geen IFC-data**. Er zijn alleen PDF-plattegronden beschikbaar. Om deze woningen mee te nemen moet ruimtedata handmatig worden ingevoerd in ruimten.csv, of moeten de PDF's eerst verwerkt worden.

## WWS berekening draaien

De woningwaardering calculator staat in `woningwaardering/`. Om de berekening handmatig te draaien (buiten de agentic verrijking om):

```python
import sys, time
if not hasattr(time, 'tzset'):  # Windows fix
    time.tzset = lambda: None
sys.path.insert(0, 'woningwaardering')

from datetime import date
from woningwaardering import Woningwaardering
from woningwaardering.vera.bvg.generated import EenhedenEenheid

wws = Woningwaardering(peildatum=date(2026, 1, 1))

with open('output/json/3004587.json', 'r') as f:
    eenheid = EenhedenEenheid.model_validate_json(f.read())

resultaat = wws.waardeer(eenheid)
print(f"Punten: {resultaat.punten}, Max huur: EUR {resultaat.maximale_huur}")
```

## Verificatie mapping

De automatische koppeling (IFC-appartement - eenheid) is gebaseerd op sequentiele type-matching: binnen elk gebouw worden hoek-appartementen op volgorde gematcht op hoek-eenheden, en std op std. Dit is een best-guess -- de exacte mapping kan geverifieerd worden aan de hand van plattegronden.

Controleer `output/mapping.csv` om te zien welk IFC-appartement (building + apt_index) gekoppeld is aan welke eenheid (bouwnummer + huisnummer). Let specifiek op:

- **B2 hoek idx=32** -- heeft 5 kamers in plaats van 6 (technische ruimte ontbreekt in IFC-model)
- **Hoek-appartementen** -- de interne volgorde van hoek-appartementen is minder zeker dan die van std

## Mappenstructuur

```
huisdata/            Brondata per project
  havensteder/       Fascinatio (IFC + Excel + PDF)
pipeline/            ETL-code
  config.py          Paden, ROOM_TYPE_MAP, COMMON_SPACES, WOZ_EUR_PER_M2
  extract_excel.py   Excel -> eenheden.csv
  extract_ifc.py     IFC -> ruimten.csv (groepering + hoek-reparatie)
  link_eenheden.py   Koppeling ruimten <-> eenheden
  csv_to_json.py     CSV's -> VERA JSON (sanitair als installaties)
  run_pipeline.py    Orchestratie (extract / json / all)
  enrich_prompt.md   Claude Code prompt voor agentic verrijking
docs/                Documentatie
  pipeline/          Per-module documentatie
  woningwaardering-input-specificatie.md
  huisdata-overzicht.md
output/              Gegenereerde bestanden (git-ignored)
  eenheden.csv       161 woningen + WWS scores
  ruimten.csv        495 kamers (66 appartementen)
  mapping.csv        66 koppelingen IFC <-> eenheid
  json/              VERA JSON per eenheid
woningwaardering/    Clone van de calculator
CLAUDE.md            Project-instructies voor Claude Code
```

## Setup

```bash
# Installeer dependencies in een venv
python -m venv .venv
.venv/Scripts/activate   # Windows
pip install -r requirements.txt
```

De IFC-bestanden zijn niet in deze repo opgenomen (te groot voor GitHub, 81-264 MB per bestand). Deze moeten lokaal worden geplaatst:

```bash
# Plaats de IFC-bestanden in huisdata/havensteder/Nieuwebouwen_Fascination_laatsteblok/:
#   - FAS_PLE_BWK-B2.ifc  (264 MB)
#   - FAS_PLE_BWK-B3.ifc  (81 MB)
#   - FAS_KAW_BWK.ifc     (213 MB, optioneel - B1 model)
```

De woningwaardering calculator is meegeleverd in de `woningwaardering/` map (clone van [woonstadrotterdam/woningwaardering](https://github.com/woonstadrotterdam/woningwaardering)).

## Quickstart

```bash
# Stap 1: Extraheer en koppel
python -m pipeline extract

# Stap 2: Verrijk (kies een optie)
# Optie A: Zeg tegen Claude Code: "follow the instructions in pipeline/enrich_prompt.md"
# Optie B: Vul handmatig aan in output/eenheden.csv en output/ruimten.csv

# Stap 3: Genereer JSON
python -m pipeline json

# Of alles in een keer (extract + json):
python -m pipeline all
```

## Documentatie

- [Pipeline documentatie](docs/pipeline/) -- hoe de pipeline werkt, per module
- [Woningwaardering input specificatie](docs/woningwaardering-input-specificatie.md) -- wat de calculator verwacht (JSON-formaat, VERA-codes, voorbeelden)
- [Huisdata overzicht](docs/huisdata-overzicht.md) -- welke brondata beschikbaar is per project
- [Enrich prompt](pipeline/enrich_prompt.md) -- instructies voor agentic verrijking met standaardwaarden
