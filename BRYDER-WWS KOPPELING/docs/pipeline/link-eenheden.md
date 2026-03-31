# link_eenheden.py -- Koppeling ruimten aan eenheden

Koppelt IFC-appartementen (uit ruimten.csv) aan wooneenheden (uit eenheden.csv) op basis van type-matching.

## Functie

### `link_ruimten_to_eenheden(eenheden_csv, ruimten_csv, mapping_csv)`

1. Leest unieke appartementen uit ruimten.csv (building + apt_type + apt_index)
2. Splitst eenheden per building (B2/B3) en type (hoek/std)
3. Matcht sequentieel: hoek-appartementen op hoek-eenheden, std op std
4. Schrijft mapping.csv en werkt ruimten.csv bij met eenheid_id en bouwnummer

**Returns:** aantal koppelingen.

## Matching-strategie

De IFC-modellen groeperen appartementen in een andere volgorde dan de Excel-bouwnummers. Een directe 1:1 mapping op index werkt niet omdat IFC hoek-appartementen aan de randen van het model clustert, terwijl Excel ze tussen de std-appartementen plaatst.

De oplossing: split binnen elk gebouw (B2/B3) de appartementen op type:
- IFC hoek-appartementen (sequentieel op apt_index) matchen op Excel hoek-eenheden (sequentieel op bouwnummer)
- Hetzelfde voor std-appartementen

Dit werkt omdat:
- Het aantal hoek en std is identiek in IFC en Excel (8 hoek + 25 std per gebouw)
- De interne volgorde binnen elk type correspondeert met de fysieke positie in het gebouw

## Output: mapping.csv

Semicolon-gescheiden verificatietabel:

| Kolom | Beschrijving |
|-------|-------------|
| building | B2 of B3 |
| apt_type | hoek of std |
| apt_index | IFC appartement-index |
| rooms | Aantal kamers |
| area_m2 | Totale oppervlakte |
| eenheid_id | Gekoppeld OGE-nummer |
| bouwnummer | Gekoppeld bouwnummer |
| huisnummer | Huisnummer |

## Bekende beperkingen

- De sequentiele matching is een best-guess. Verificatie via plattegronden wordt aanbevolen.
- B2 hoek-appartement idx=32 mist een technische ruimte (room 184 was orphaned in het IFC-model).
- B1-woningen (95 stuks) hebben geen IFC-data en worden niet gekoppeld.
