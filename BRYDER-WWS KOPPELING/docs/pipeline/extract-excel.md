# extract_excel.py -- Excel-extractie

Leest het Excel-bestand met eenheden-registratie en schrijft `eenheden.csv`.

## Functie

### `extract_eenheden(excel_path, output_path)`

Leest het eerste werkblad van het Excel-bestand. Elke rij is een eenheid (woning of bedrijfsruimte).

**Filtering:** Rijen zonder `bouwnummer` worden overgeslagen -- dit zijn bedrijfsruimten.

**Pandsoort-bepaling:** Op basis van het `type overzicht`-veld:
- `B1...` -> `EGW` (eengezinswoning / laagbouw)
- `B2...` / `B3...` -> `MGW` (meergezinswoning / appartementen)

## Output: eenheden.csv

Semicolon-gescheiden, UTF-8 met BOM. 26 kolommen:

| Kolom | Bron | Beschrijving |
|-------|------|-------------|
| `eenheid_id` | Excel (OGEnummer) | Unieke identifier |
| `bouwnummer` | Excel | Bouwnummer |
| `straat` | Excel | Straatnaam |
| `huisnummer` | Excel | Huisnummer |
| `huisletter` | Excel (Huis Letter) | Huisletter |
| `huisnummertoevoeging` | Excel | Toevoeging |
| `postcode` | Excel | Postcode |
| `plaats` | Excel | Plaatsnaam |
| `type_overzicht` | Excel | Type-code (B1/B2/B3 + variant) |
| `cluster_naam` | Excel | Clusternaam |
| `pand_id` | Excel | Pand ID |
| `bag_verblijfsobject` | Excel (BAG) | BAG verblijfsobject ID |
| `bag_nummeraanduiding` | Excel | BAG nummeraanduiding |
| `woningwaarderingstelsel` | Vast: `ZEL` | Stelseltype |
| `pandsoort` | Afgeleid | EGW of MGW |
| `bouwjaar` | **Handmatig** | Bouwjaar van het pand |
| `klimaatbeheersing` | **Handmatig** | IND of GEM |
| `woz_waarde` | **Handmatig** | WOZ-waarde in euro's |
| `woz_peildatum` | **Handmatig** | Peildatum (YYYY-MM-DD) |
| `energielabel` | **Handmatig** | A++++, A+++, ..., G |
| `energieprestatie_soort` | **Handmatig** | NTA of EI |
| `energieprestatie_waarde` | **Handmatig** | Numerieke waarde |
| `energieprestatie_begindatum` | **Handmatig** | Ingangsdatum |
| `energieprestatie_einddatum` | **Handmatig** | Vervaldatum |
| `monument` | **Handmatig** | RM, GM, PM, BSG of leeg |
| `gebruiksoppervlakte` | **Handmatig** | Oppervlakte in m2 |

Kolommen gemarkeerd met **Handmatig** worden leeg geschreven en moeten handmatig worden aangevuld.
