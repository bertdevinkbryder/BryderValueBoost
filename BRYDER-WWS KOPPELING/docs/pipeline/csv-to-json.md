# csv_to_json.py -- CSV naar JSON conversie

Leest `eenheden.csv` en `ruimten.csv` en genereert per eenheid een VERA-conform JSON-bestand.

## Functie

### `convert_to_json(eenheden_csv, ruimten_csv, output_dir)`

1. Leest beide CSV's (semicolon-gescheiden, UTF-8 BOM)
2. Groepeert ruimten per `eenheid_id`
3. Genereert per eenheid met gekoppelde ruimten een JSON-bestand
4. Eenheden zonder ruimten worden overgeslagen

**Returns:** aantal gegenereerde bestanden.

## JSON-structuur

Elk bestand volgt het VERA `EenhedenEenheid` model. Zie [woningwaardering-input-specificatie.md](../woningwaardering-input-specificatie.md) voor de volledige specificatie.

### Eenheid-niveau

Uit eenheden.csv:

| CSV-kolom | JSON-veld | Opmerkingen |
|-----------|-----------|-------------|
| `eenheid_id` | `id` | |
| `woningwaarderingstelsel` | `woningwaarderingstelsel` | Referentiedata-object |
| `bouwjaar` | `bouwjaar` | Integer |
| `straat`, `huisnummer`, etc. | `adres` | Genest object |
| `bag_verblijfsobject` | `adresseerbaarObjectBasisregistratie` | Met bagIdentificatie |
| `pandsoort` | `panden[0].soort` | EGW -> Eengezinswoning |
| `klimaatbeheersing` | `klimaatbeheersing` | IND -> Individueel |
| `woz_waarde`, `woz_peildatum` | `wozEenheden[0]` | |
| `energielabel`, etc. | `energieprestaties[0]` | Met soort, waarde, status=DEF |
| `monument` | `monumenten` | RM, GM, PM of BSG |
| `gebruiksoppervlakte` | `gebruiksoppervlakte` | Integer |

### Ruimte-niveau

Uit ruimten.csv, per ruimte:

| CSV-kolom | JSON-veld | Opmerkingen |
|-----------|-----------|-------------|
| `ruimte_id` | `id` | |
| `naam` | `naam` | |
| `soort_code`, `soort_naam` | `soort` | Referentiedata |
| `detail_soort_code`, `detail_soort_naam` | `detailSoort` | Referentiedata |
| `oppervlakte_m2` | `oppervlakte` | Float |
| `verwarmd` | `verwarmd` | Boolean |
| `inhoud_m3` | `inhoud` | Optioneel |
| `hoogte_mm` | `hoogte` | mm -> m conversie |
| `verkoeld` | `verkoeld` | Alleen als ja |
| `afsluitbaar` | `afsluitbaar` | Boolean, optioneel |
| `bouwlaag` | `bouwlaag.nummer` | Optioneel |
| `gedeeld_met_aantal` | `gedeeldMetAantalEenheden` | Integer, optioneel |

### Bouwkundige elementen

Gegenereerd uit de `sanitair` en `aanrecht_lengte_mm` kolommen in ruimten.csv.

**Sanitair** -- kommagescheiden codes in de `sanitair` kolom:

| Code | Naam | Soort |
|------|------|-------|
| DOU | Douche | SAN (Sanitaire voorziening) |
| BAD | Bad | SAN |
| WAS | Wastafel | SAN |
| CLO | Toilet | SAN |
| STO | Staand toilet | SAN |

Elk sanitair-item wordt een apart bouwkundig element met een gegenereerd ID: `{ruimte_id}_{code}_{index}`.

**Aanrecht** -- als `aanrecht_lengte_mm` is ingevuld:

```json
{
  "id": "{ruimte_id}_AAN",
  "naam": "Aanrecht",
  "soort": {"code": "KEU", "naam": "Keuken voorziening"},
  "detailSoort": {"code": "AAN", "naam": "Aanrecht"},
  "lengte": 2000
}
```

Lengte is in millimeters.

## Output

Bestanden worden geschreven naar `output/json/{eenheid_id}.json`, een per eenheid.
