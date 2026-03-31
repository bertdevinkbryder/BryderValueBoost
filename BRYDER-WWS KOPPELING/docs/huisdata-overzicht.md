# Huisdata - Overzicht brondatastructuur

Dit document beschrijft de beschikbare data in de `huisdata/` map, georganiseerd per opdrachtgever/project. Het doel is inzicht te geven in welke gegevens beschikbaar zijn en hoe ze gestructureerd zijn, zodat ze gekoppeld kunnen worden aan de woningwaardering calculator.

---

## Mappenstructuur

```
huisdata/
├── havensteder/
│   └── Nieuwebouwen_Fascination_laatsteblok/
│       ├── FAS_KAW_BWK.ifc                   (213 MB - Archicad bouwkundig model)
│       ├── FAS_PLE_BWK-B2.ifc                 (264 MB - Revit appartementen blok B2)
│       ├── FAS_PLE_BWK-B3.ifc                 (81 MB  - Revit appartementen blok B3)
│       ├── fascinatio nieuwbouw 20250218.xlsx  (eenheden-registratie)
│       ├── Huisnummerbesluit (...).pdf         (officieel huisnummerbesluit)
│       └── 1) bouwkundig tekenwerk B1/
│           ├── TO.1.00 Begane grond.pdf        (plattegronden per verdieping)
│           ├── TO.1.01 Eerste verdieping.pdf
│           ├── ... (t/m TO.1.09)
│           ├── TO.2.xx Gevels.pdf
│           ├── TO.3.xx Doorsneden.pdf
│           ├── TO.4 Impressies.pdf
│           └── TO.5 Details.pdf
├── wonenzuid/                                  (leeg)
└── woonstichtinghulst/
    ├── Onder de toren; wijzigingen_RG_22-01-2026.pdf
    └── 2025-05-14 Verstuurd WSH en vKerckhoven/
        ├── 2024 013A_DO_01-xx Situatie/Plattegronden.pdf
        ├── 2024 013A_DO_02-xx Gevels.pdf
        ├── 2024 013A_DO_03-xx Doorsneden.pdf
        ├── 2024 013A_DO_11-00-GBO.pdf          (gebruiksoppervlakte overzicht)
        ├── 2024 013A_DO_13-00 t/m 13-07 App. A-G.pdf  (plattegronden per appartement)
        └── 2024 013A_DO_13-11-Doorsneden kappen.pdf
```

---

## 1. Havensteder - Fascinatio laatsteblok

### Project

- **Locatie**: Fascinatio Boulevard, Capelle aan den IJssel
- **Opdrachtgever**: Havensteder
- **Architect**: KAW Architecten, Rotterdam (projectnr 210091)
- **Type**: Nieuwbouw, 161 woningen + 2 bedrijfsruimten
- **Gebouwen**: Blok B1 (laagbouw), Blok B2 (appartementen), Blok B3 (appartementen)

---

### 1.1 Excel: `fascinatio nieuwbouw 20250218.xlsx`

De meest gestructureerde databron. Bevat registratiegegevens van alle 163 eenheden.

#### Kolommen

| Kolom | Type | Beschrijving | Voorbeeld |
|-------|------|-------------|-----------|
| `OGEnummer` | integer | Intern eenheid-ID | `3004587` |
| `straat` | string | Straatnaam | `Fascinatio Boulevard` |
| `Huisnummer` | integer | Huisnummer | `1400` |
| `Huis Letter` | string | Huisletter (alleen bedrijfsruimten) | `A`, `B` |
| `Huisnummertoevoeging` | string | Toevoeging | `01` |
| `Eenheidaanduiding` | string | Eenheid type-aanduiding | `NVZ01 INPAND` |
| `Huisnummertoevoegsel` | string | Volledig toevoegsel | `A 01 NVZ01 INPAND` |
| `Postcode` | string | Postcode | `2909 VD` |
| `Plaats` | string | Plaatsnaam | `CAPELLE AAN DEN IJSSEL` |
| `Cluster Nummer Algemeen` | string | Cluster-ID | |
| `Cluster Naam Algemeen` | string | Clusternaam | `Fascinatio 1400-1464 WON` |
| `bouwnummer` | integer | Bouwnummer (1-161) | `1` |
| `type overzicht` | string | Woningtype-code | `B1-laagbouw` |
| `Pand_id` | string | BAG Pand-ID | |
| `BAG` | string | BAG Verblijfsobject-ID | |
| `BAG Nummeraanduiding` | string | BAG Nummeraanduiding-ID | |
| `berging nr / locatie` | string | Berging info | `berging inpandig in de woning` |

#### Clusters

| Cluster | Aantal | Type |
|---------|--------|------|
| Fascinatio 1400-1464 WON | 33 | Woningen |
| Fascinatio 1466-1530 WON | 33 | Woningen |
| Fascinatio 1466-1530 BDR | 2 | Bedrijfsruimte/berging |
| Fascinatio 1532-1664 WON | 67 | Woningen |
| Fascinatio 1666-1720 WON | 28 | Woningen |

#### Woningtypen (11 varianten)

| Type | Aantal | Beschrijving |
|------|--------|-------------|
| `B1` | 16 | Standaard rijwoning type 1 |
| `B1-hoek` | 4 | Hoekwoning B1 |
| `B1-kop` | 4 | Kopwoning B1 |
| `B1-laagbouw` | 28 | Laagbouw variant B1 |
| `B1-schuin` | 30 | Schuine variant B1 |
| `B1-schuin kop` | 9 | Schuine kopwoning B1 |
| `B1-sp` | 4 | Gespiegelde variant B1 |
| `B2` | 25 | Standaard appartement type 2 |
| `B2 hoek` | 8 | Hoek-appartement B2 |
| `B3` | 25 | Standaard appartement type 3 |
| `B3 hoek` | 8 | Hoek-appartement B3 |

#### Relevantie voor WWS

De Excel bevat **adresgegevens** en **BAG-identificaties** die nodig zijn voor de woningwaardering, maar **geen** ruimte-informatie (oppervlakten, kamers, sanitair). Die moet uit de IFC-bestanden of tekeningen komen.

---

### 1.2 IFC-bestanden

Drie BIM-modellen bevatten de gebouwinformatie in IFC2X3-formaat.

#### Bestandsoverzicht

| Bestand | Software | Grootte | Beschrijving |
|---------|----------|---------|-------------|
| `FAS_KAW_BWK.ifc` | Archicad 26 | 213 MB | Bouwkundig model (muren, deuren, ramen) |
| `FAS_PLE_BWK-B2.ifc` | Revit 2023 | 264 MB | Appartementenblok B2 met ruimten |
| `FAS_PLE_BWK-B3.ifc` | Revit 2023 | 81 MB | Appartementenblok B3 met ruimten |

#### Entiteiten per bestand

| Entiteit | KAW (B1) | PLE (B2) | PLE (B3) | Totaal |
|----------|----------|----------|----------|--------|
| `IfcBuilding` | 1 | 1 | 1 | 3 |
| `IfcBuildingStorey` | 11 | 13 | 13 | 37 |
| `IfcSpace` | 0 | 271 | 278 | 549 |
| `IfcDoor` | 764 | 524 | 518 | 1.806 |
| `IfcWindow` | 302 | 930 | 942 | 2.174 |
| `IfcWall` | 2.247 | 2 | 5 | 2.254 |
| `IfcSanitaryTerminal` | 0 | 0 | 0 | 0 |
| `IfcPropertySet` | - | - | - | 237.735 |
| `IfcElementQuantity` | - | - | - | 57.329 |

**Belangrijk**: Het KAW-model (B1) bevat **geen** `IfcSpace`-entiteiten. Ruimten zitten alleen in de Revit-modellen (B2 en B3). Sanitaire voorzieningen (`IfcSanitaryTerminal`) ontbreken in alle drie de bestanden.

#### IfcSpace structuur (B2 & B3)

Elke `IfcSpace` bevat:

```
IFCSPACE('GUID', #owner, 'Naam', $, $, #placement, #shape, 'LongName', .ELEMENT., .INTERNAL., $)
```

| Veld | Beschrijving | Voorbeeld |
|------|-------------|-----------|
| GUID | Uniek IFC-ID | `1SOfNgAlzCshapJMjrHp$U` |
| Name | Ruimtenummer | `0.174` |
| LongName | Ruimtenaam (leesbaar) | `Fietsenstalling` |
| CompositionType | Altijd `.ELEMENT.` | |
| InternalOrExternal | Altijd `.INTERNAL.` | |

#### Beschikbare ruimtetypen in IFC

| LongName in IFC | Vertaling | WWS-equivalent |
|-----------------|-----------|----------------|
| `woonkamer / keuken` | Woonkamer/keuken | VTK: WOO + KEU |
| `slaapkamer 1` | Slaapkamer | VTK: SLA |
| `slaapkamer 2` | Slaapkamer | VTK: SLA |
| `badkamer / toilet` | Badkamer/toilet | VTK: BAD |
| `hal` | Hal | VRK: HAL |
| `berging / techniek` | Berging/technische ruimte | OVR: BER / TEC |
| `MK warm` | Meterkast (warm) | OVR: MET |
| `MK koud` | Meterkast (koud) | OVR: MET |
| `entree` | Entree | VRK: HAL |
| `technische ruimte` | Technische ruimte | OVR: TEC |
| `Fietsenstalling` | Fietsenstalling | OVR (gemeenschappelijk) |
| `cvz kast` | CVZ-kast | OVR: TEC |

#### Beschikbare metingen per ruimte (BaseQuantities)

Elke `IfcSpace` heeft een `IfcElementQuantity` genaamd "BaseQuantities" met:

| Quantity | Type | Eenheid | Beschrijving |
|----------|------|---------|-------------|
| `NetFloorArea` | Area | m2 | Netto vloeroppervlakte |
| `GrossFloorArea` | Area | m2 | Bruto vloeroppervlakte |
| `Height` | Length | mm | Hoogte van de ruimte |
| `GrossPerimeter` | Length | mm | Omtrek (niet altijd aanwezig) |
| `GrossVolume` | Volume | m3 | Bruto volume |

#### Voorbeeld: ruimte uit IFC

```
IfcSpace:
  GUID: 1SOfNgAlzCshapJMjrHp$U
  Name: "0.174"
  LongName: "slaapkamer 2"

  BaseQuantities:
    NetFloorArea: 12.57 m2
    GrossFloorArea: 12.57 m2
    Height: 2438.4 mm
    GrossVolume: 30.64 m3
```

#### Property Sets per ruimte

| PropertySet | Inhoud |
|-------------|--------|
| `Pset_AirSideSystemInformation` | Name (ruimtenaam) |
| `Pset_ProductRequirements` | Name, Category ("Rooms") |
| `Pset_SpaceCommon` | Reference (bijv. "slaapkamer 2 0.07.37"), Category |

---

### 1.3 PDF Tekeningen (Blok B1)

29 PDF-bestanden met bouwkundige tekeningen op schaal 1:100 (A0-formaat).

#### Categorieën

| Prefix | Aantal | Inhoud |
|--------|--------|--------|
| TO.1.xx | 10 | Plattegronden (begane grond t/m dakverdieping) |
| TO.2.xx | 3 | Gevels (noord, zuid, oost, west) |
| TO.3.xx | 7 | Doorsneden (A-A t/m K-K) |
| TO.4 | 1 | Impressies |
| TO.5 | 1 | Details |

#### Extraheerbare data uit plattegronden

De plattegrondtekeningen bevatten per woning:

| Gegeven | Voorbeeld | Beschrijving |
|---------|-----------|-------------|
| Woningtype | `AG-06` | Type-aanduiding |
| GO (GBO) | `49.7 m2` | Gebruiksoppervlakte totaal |
| Kamernamen | `woonkamer`, `slaapkamer 1` | Per ruimte |
| Kameroppervlakten | `23.5 m2` | Per ruimte |
| Huisnummers | `1532`, `1534`, ... | Per woning |
| Buitenruimte | `5.5 m2` | Balkon/terras oppervlakte |
| Afmetingen | In mm | Maat-to-maat |

**Extractie-moeilijkheid**: Matig. Tekst is aanwezig als CAD-tekst en extraheerbaar via PyMuPDF, maar ruimtelijk verspreid over het tekenblad. Vereist spatiale groepering.

---

### 1.4 Huisnummerbesluit PDF

Officieel besluit van gemeente Capelle aan den IJssel (25 maart 2024).

| Gegeven | Waarde |
|---------|--------|
| Adressen | Fascinatio Boulevard 1468A01, 1468B01 |
| Buurtcode | 05020991 |
| ID openbare ruimte | 0502300000002528 |
| Gemeente | Capelle aan den IJssel |

---

## 2. Woonstichting Hulst - Herbestemming Refugium Baudeloo

### Project

- **Locatie**: Baudeloo 20, 4561ES Hulst
- **Opdrachtgever**: Woonstichting Hulst
- **Architect**: VG architecten, Sas van Gent (projectnr 2024-013A)
- **Type**: Herbestemming (verbouw monument naar 7 appartementen A t/m G)
- **Fase**: Definitief Ontwerp (DO)

### 2.1 GBO-overzicht (`2024 013A_DO_11-00-GBO.pdf`)

Samenvatting gebruiksoppervlakte per appartement. Kleurgecodeerd op stahoogte (relevant voor WWS bij schuine daken).

| Appartement | GBO per laag | Totaal GBO |
|-------------|-------------|------------|
| A | 19 + 46 + 18 + 46 m2 | **129 m2** |
| B | 52 m2 | **52 m2** |
| C | 54 + 14 m2 | **68 m2** |
| D | 56 m2 | **56 m2** |
| E | 69 + 5 m2 | **74 m2** |
| F | 80 m2 | **80 m2** |
| G | 34 + 24 m2 | **58 m2** |

#### Hoogtezonering (kleuren)

| Zone | Stahoogte | WWS-relevantie |
|------|-----------|----------------|
| Zone 1 | > 2600 mm | Telt volledig mee |
| Zone 2 | > 2100 mm | Telt volledig mee |
| Zone 3 | > 1500 mm | Telt deels mee (schuine daken) |
| < 1500 mm | < 1500 mm | Telt niet mee |

### 2.2 Appartement-plattegronden (App. A t/m G)

Per appartement een gedetailleerde plattegrond (schaal 1:40) met:

| Gegeven | Beschrijving | Voorbeeld |
|---------|-------------|-----------|
| Ruimtecodes | Genummerd per appartement | `a.01`, `a.02`, `a.03` |
| Ruimtenamen | Nederlands | `keuken`, `zitkamer`, `eetkamer` |
| Oppervlakten | In m2 | `13 m2`, `19 m2`, `31 m2` |
| Afmetingen | In mm | `5120`, `2403` |
| Bouwspecificaties | Isolatiewaarden, wandopbouw | `Rc = 4.7 m2K/W` |
| Bestaand/nieuw | Onderscheid renovatie | Markering in legenda |

**Extractie-moeilijkheid**: Matig. CAD-tekst is extraheerbaar maar ruimtelijk verspreid.

### 2.3 Overige tekeningen

- **Situatietekening**: Locatie in stedenbouwkundig verband
- **Bestaande/nieuwe plattegronden**: Sloop- en nieuwbouwoverzicht
- **Geveltekeningen**: Bestaand en nieuw
- **Doorsneden**: Hoogte-informatie, kapconstructies
- **3D Aanzichten**: Visualisaties

---

## 3. Woonstichting Hulst - Onder de Toren

### Project

- **Type**: Verbouw/herontwikkeling naar lofts
- **Bron**: 1 samengesteld PDF-tekenblad

### 3.1 Loft-specificaties (`Onder de toren; wijzigingen_RG_22-01-2026.pdf`)

**Let op**: Dit PDF bevat **geen extraheerbare tekst** (geexporteerd als curves/outlines). Data-extractie vereist OCR.

Het blad bevat per loft een specificatietabel met:

| Kolom | Beschrijving | Voorbeeld |
|-------|-------------|-----------|
| `nr.` | Ruimtenummer | `0.01` |
| `ruimte` | Ruimtenaam | `hal`, `woonkamer/keuken` |
| `ruimtesoort` | Type ruimte | `verkeersruimte`, `verblijfsruimte` |
| `GBO` | Oppervlakte in m2 | `3.0`, `61.9` |

#### Bekende lofts

**Loft 6:**

| Nr. | Ruimte | Ruimtesoort | GBO |
|-----|--------|-------------|-----|
| 0.01 | woonkamer/keuken | verblijfsruimte | 61.9 m2 |
| 0.02 | slaapkamer | verblijfsruimte | 19.5 m2 |
| 0.03 | gang | verkeersruimte | 6.1 m2 |
| 0.04 | berging | functieruimte | 2.7 m2 |
| 0.05 | toilet | toiletruimte | 1.5 m2 |
| 0.06 | badkamer | badruimte | 4.0 m2 |

**Loft 7:**

| Nr. | Ruimte | Ruimtesoort | GBO |
|-----|--------|-------------|-----|
| 0.01 | hal | verkeersruimte | 3.0 m2 |
| 0.02 | loft | verblijfsruimte | 106.3 m2 |
| 0.03 | berging | functieruimte | 2.7 m2 |
| 0.04 | toilet | toiletruimte | 1.5 m2 |
| 0.05 | badkamer | badruimte | 4.0 m2 |

**Loft 8:**

| Nr. | Ruimte | Ruimtesoort | GBO |
|-----|--------|-------------|-----|
| 0.01 | hal | verkeersruimte | 3.0 m2 |
| 0.02 | toilet | toiletruimte | 2.3 m2 |
| 0.03 | badkamer | badruimte | 5.1 m2 |
| 0.04 | berging | functieruimte | 4.3 m2 |
| 0.05 | loft | verblijfsruimte | 60.6 m2 |

---

## Samenvatting: beschikbare data per bron

| Databron | Adressen | Ruimten | Oppervlakten | Sanitair | Keuken | Energie | WOZ | BAG |
|----------|----------|---------|-------------|----------|--------|---------|-----|-----|
| **Excel (Havensteder)** | Ja | Nee | Nee | Nee | Nee | Nee | Nee | Ja |
| **IFC B2/B3 (Havensteder)** | Nee | Ja (549) | Ja (m2, m3) | Nee | Nee | Nee | Nee | Nee |
| **IFC KAW (Havensteder)** | Nee | Nee | Nee | Beperkt | Nee | Nee | Nee | Nee |
| **PDF plattegronden B1** | Ja | Ja | Ja (per kamer) | Nee | Nee | Nee | Nee | Nee |
| **PDF GBO (Hulst)** | Nee | Nee | Ja (totaal) | Nee | Nee | Nee | Nee | Nee |
| **PDF App. A-G (Hulst)** | Ja | Ja | Ja (per kamer) | Nee | Nee | Nee | Nee | Nee |
| **PDF Onder de Toren** | Nee | Ja | Ja (per kamer) | Nee | Nee | Nee | Nee | Nee |

### Wat ontbreekt in alle bronnen

De volgende gegevens die de woningwaardering calculator nodig heeft, zijn **niet** aanwezig in de huisdata:

| Ontbrekend gegeven | Benodigde actie |
|-------------------|-----------------|
| **WOZ-waarden** | Opvragen bij gemeente/belastingdienst |
| **Energieprestatie / energielabel** | Opvragen bij RVO / EP-Online |
| **Sanitaire voorzieningen** (douche, bad, toilet, wastafel) | Afleiden uit plattegronden of handmatig invoeren |
| **Keuken aanrechtlengte** | Afleiden uit plattegronden of bestek |
| **Verwarmingstype** (individueel/gemeenschappelijk) | Afleiden uit bestek of IFC installatie-model |
| **Monumentstatus** | Opvragen bij Rijksdienst voor Cultureel Erfgoed |
| **Buitenruimte-afmetingen** (lengte x breedte) | Deels beschikbaar in PDF tekeningen |
| **`verwarmd` per ruimte** | Afleiden uit installatie-ontwerp of aannames |

---

## Bronformaten en extractiemethoden

| Formaat | Bestanden | Extractiemethode | Complexiteit |
|---------|-----------|-------------------|-------------|
| **Excel (.xlsx)** | 1 | `openpyxl` / `pandas` | Eenvoudig |
| **IFC (.ifc)** | 3 | `ifcopenshell` (Python) | Matig |
| **PDF (met tekst)** | ~25 | `PyMuPDF` / `pdfplumber` | Matig-Complex |
| **PDF (zonder tekst)** | 1 | OCR (`pytesseract`) | Complex |
