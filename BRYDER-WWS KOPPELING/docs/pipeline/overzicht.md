# Pipeline - Overzicht

De pipeline extraheert gebouwdata uit IFC-modellen en Excel-bestanden, zet deze om in tussentijdse CSV-bestanden, en converteert die uiteindelijk naar VERA-conforme JSON voor de woningwaardering calculator.

## Architectuur

```
pipeline/
  __main__.py        Entry point (roept run_pipeline.main aan)
  run_pipeline.py    Orchestratie: extract en json stappen
  config.py          Configuratie: paden, mappings, constanten
  extract_excel.py   Excel -> eenheden.csv
  extract_ifc.py     IFC -> ruimten.csv (met hoek-reparatie)
  link_eenheden.py   Koppelt ruimten aan eenheden (type-matching)
  csv_to_json.py     CSV's -> JSON per eenheid
```

## Datastroom

```
  Excel-registratie                    eenheden.csv
  (OGE-nummers, adressen,    ──────>  (1 rij per woning,
   bouwnummers, BAG-ids)               lege kolommen voor
                                        handmatige aanvulling)

  IFC-modellen B2 + B3                ruimten.csv
  (IfcSpace entiteiten        ──────>  (1 rij per kamer,
   met BaseQuantities)                  gegroepeerd in
                                        appartementen)
                                           │
                              link_eenheden │  type-matching
                                           v
                                       mapping.csv
                                       + ruimten.csv bijgewerkt
                                         met eenheid_id/bouwnummer

  eenheden.csv + ruimten.csv          output/json/
  (na handmatige verrijking)  ──────>  (1 JSON per eenheid,
                                        VERA EenhedenEenheid
                                        formaat)
```

## Gebruik

```bash
# Beide stappen
python -m pipeline all

# Alleen extractie
python -m pipeline extract

# Alleen JSON-conversie (na handmatig aanvullen CSV's)
python -m pipeline json
```

## CSV als tussenformaat

De keuze voor CSV als tussenformaat is bewust: er zijn gegevens die niet uit de brondata te halen zijn en handmatig opgezocht moeten worden. Door eerst naar CSV te schrijven kunnen deze velden in een spreadsheet-editor worden aangevuld voordat de definitieve JSON gegenereerd wordt.

**Handmatig aan te vullen in eenheden.csv:**
- `bouwjaar` -- bouwjaar van het pand
- `klimaatbeheersing` -- IND (individueel) of GEM (gemeenschappelijk)
- `woz_waarde`, `woz_peildatum` -- WOZ-waarde en peildatum
- `energielabel`, `energieprestatie_soort`, etc. -- energieprestatie
- `monument` -- RM, GM, PM of BSG indien van toepassing
- `gebruiksoppervlakte` -- gebruiksoppervlakte in m2

**Handmatig aan te vullen in ruimten.csv:**
- `sanitair` -- kommagescheiden codes (DOU, BAD, WAS, CLO, STO)
- `aanrecht_lengte_mm` -- aanrechtlengte in millimeters
- `bouwlaag` -- verdiepingsnummer
- `afsluitbaar` -- ja/nee
- `gedeeld_met_aantal` -- aantal eenheden waarmee de ruimte gedeeld wordt

**Automatisch ingevuld door link_eenheden.py:**
- `eenheid_id` -- koppeling naar eenheden.csv (OGE-nummer)
- `bouwnummer` -- bouwnummer van de woning

De koppeling is gebaseerd op type-matching: hoek-appartementen worden sequentieel gematcht op hoek-eenheden, en std op std, per gebouw. Zie [link-eenheden.md](link-eenheden.md) en [mapping.csv](../../output/mapping.csv) voor verificatie.

## Modules

- [config.md](config.md) -- Configuratie en mappings
- [extract-excel.md](extract-excel.md) -- Excel-extractie
- [extract-ifc.md](extract-ifc.md) -- IFC-extractie en appartement-groepering
- [link-eenheden.md](link-eenheden.md) -- Koppeling ruimten aan eenheden
- [csv-to-json.md](csv-to-json.md) -- CSV naar JSON conversie
