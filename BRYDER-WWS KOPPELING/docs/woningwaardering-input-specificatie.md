# Woningwaardering Calculator - Input Specificatie

De woningwaardering calculator verwacht een JSON-object dat een wooneenheid beschrijft conform het VERA-model (`EenhedenEenheid`). Dit document beschrijft alle velden, hun types, toegestane waarden en onderlinge relaties.

---

## Gebruik

```python
from woningwaardering import Woningwaardering
from woningwaardering.vera.bvg.generated import EenhedenEenheid
from datetime import date

# Laad input
with open("eenheid.json") as f:
    eenheid = EenhedenEenheid.model_validate_json(f.read())

# Bereken
wws = Woningwaardering(peildatum=date(2025, 7, 1))  # optioneel, default = vandaag
resultaat = wws.waardeer(eenheid)
```

De calculator detecteert automatisch of het om een **zelfstandige** (`ZEL`) of **onzelfstandige** (`ONZ`) woonruimte gaat op basis van het veld `woningwaarderingstelsel`.

---

## Top-level structuur: EenhedenEenheid

| Veld | Type | Verplicht | Beschrijving |
|------|------|-----------|-------------|
| `id` | `string` | Ja | Unieke identifier van de eenheid |
| `bouwjaar` | `integer` | Ja | Bouwjaar van het pand |
| `woningwaarderingstelsel` | `Referentiedata` | Ja | Welk stelsel gebruikt wordt (zie codes) |
| `klimaatbeheersing` | `Referentiedata[]` | Nee | Type verwarming/koeling |
| `adres` | `EenhedenEenheidadres` | Nee | Adresgegevens |
| `adresseerbaarObjectBasisregistratie` | `object` | Nee | BAG-registratie koppeling |
| `panden` | `EenhedenPand[]` | Nee | Pandgegevens (type woning) |
| `wozEenheden` | `EenhedenWozEenheid[]` | Nee | WOZ-waarden per peildatum |
| `energieprestaties` | `EenhedenEnergieprestatie[]` | Nee | Energielabels en -indices |
| `gebruiksoppervlakte` | `integer` | Nee | Totale gebruiksoppervlakte in m2 |
| `monumenten` | `Referentiedata[]` | Nee | Monumentstatus(sen) |
| `ruimten` | `EenhedenRuimte[]` | Ja | Alle ruimten in de eenheid (kern van de berekening) |
| `doelgroep` | `Referentiedata` | Nee | Doelgroep (bijv. zorgwoning) |

### Voorbeeld minimale structuur

```json
{
  "id": "12006000004",
  "bouwjaar": 1981,
  "woningwaarderingstelsel": {
    "code": "ZEL",
    "naam": "Zelfstandige woonruimte"
  },
  "ruimten": [ ... ]
}
```

---

## Referentiedata (herbruikbaar patroon)

Vrijwel alle gecodeerde velden gebruiken hetzelfde `Referentiedata`-patroon:

```json
{
  "code": "ZEL",
  "naam": "Zelfstandige woonruimte"
}
```

Beide velden (`code` en `naam`) worden verwacht. De `code` is bepalend voor de logica; de `naam` is beschrijvend.

---

## Woningwaarderingstelsel

Bepaalt welk puntenstelsel wordt gebruikt.

| Code | Naam |
|------|------|
| `ZEL` | Zelfstandige woonruimten |
| `ONZ` | Onzelfstandige woonruimten |
| `STA` | Standplaatsen |
| `WOO` | Woonwagens |

---

## Klimaatbeheersing

Type verwarming/koeling van de woning. Array van Referentiedata.

| Code | Naam |
|------|------|
| `IND` | Individueel |
| `GEM` | Gemeenschappelijk |

```json
"klimaatbeheersing": [
  {
    "code": "IND",
    "naam": "Individueel"
  }
]
```

---

## Adres (`EenhedenEenheidadres`)

| Veld | Type | Beschrijving |
|------|------|-------------|
| `straatnaam` | `string` | Straatnaam |
| `huisnummer` | `string` | Huisnummer |
| `huisnummerToevoeging` | `string` | Huisnummer toevoeging (bijv. "a", "c") |
| `postcode` | `string` | Postcode |
| `woonplaats` | `object` | Object met `naam` (en optioneel `code`) |

```json
"adres": {
  "straatnaam": "Voorbeeldstraat",
  "huisnummer": "42",
  "huisnummerToevoeging": "c",
  "postcode": "3011AA",
  "woonplaats": {
    "naam": "ROTTERDAM"
  }
}
```

---

## Adresseerbaar Object Basisregistratie (BAG)

Koppeling aan de Basisregistratie Adressen en Gebouwen.

| Veld | Type | Beschrijving |
|------|------|-------------|
| `id` | `string` | Intern ID |
| `bagIdentificatie` | `string` | BAG-identificatiecode |
| `bag_gebruikers_oppervlakte` | `float` | BAG gebruiksoppervlakte in m2 (optioneel) |

---

## Panden (`EenhedenPand[]`)

Beschrijft het gebouw/de gebouwen waar de eenheid in zit.

| Veld | Type | Beschrijving |
|------|------|-------------|
| `soort` | `Referentiedata` | Type pand |
| `idExtern` | `string` | Extern ID (optioneel) |
| `liftAanwezig` | `boolean` | Of er een lift aanwezig is (optioneel) |

### Pandsoort codes

| Code | Naam |
|------|------|
| `EGW` | Eengezinswoning |
| `MGW` | Meergezinswoning |

```json
"panden": [
  {
    "soort": {
      "code": "MGW",
      "naam": "Meergezinswoning"
    }
  }
]
```

---

## WOZ-eenheden (`EenhedenWozEenheid[]`)

WOZ-waarden per waardepeildatum. Meerdere jaren kunnen worden opgegeven; de calculator selecteert de juiste op basis van de peildatum.

| Veld | Type | Beschrijving |
|------|------|-------------|
| `waardepeildatum` | `string` (date: `YYYY-MM-DD`) | Waardepeildatum |
| `vastgesteldeWaarde` | `float` | Vastgestelde WOZ-waarde in euro's |

```json
"wozEenheden": [
  {
    "waardepeildatum": "2023-01-01",
    "vastgesteldeWaarde": 309000
  },
  {
    "waardepeildatum": "2024-01-01",
    "vastgesteldeWaarde": 318000
  }
]
```

---

## Energieprestaties (`EenhedenEnergieprestatie[]`)

Energielabels en energie-indexen van de woning.

| Veld | Type | Beschrijving |
|------|------|-------------|
| `soort` | `Referentiedata` | Type energieprestatie |
| `status` | `Referentiedata` | Status (bijv. definitief) |
| `begindatum` | `string` (date) | Ingangsdatum |
| `einddatum` | `string` (date) | Einddatum |
| `registratiedatum` | `string` (datetime) | Registratiedatum |
| `label` | `Referentiedata` | Energielabel (A t/m G, of A+, A++ etc.) |
| `waarde` | `string` | Numerieke waarde van de index |

### Energieprestatiesoort codes

| Code | Naam | Beschrijving |
|------|------|-------------|
| `NTA` | Energielabel conform NTA8800 | Huidige standaard |
| `EI` | Energie-index | Oudere methode |
| `MEEL` | Meetinstructie energielabel | |
| `EPV` | Energieprestatievergoeding | |

### Energielabel codes

| Code | Naam |
|------|------|
| `A+++` | A+++ |
| `A++` | A++ |
| `A+` | A+ |
| `A` | A |
| `B` | B |
| `C` | C |
| `D` | D |
| `E` | E |
| `F` | F |
| `G` | G |

### Status codes

| Code | Naam |
|------|------|
| `DEF` | Definitief |

```json
"energieprestaties": [
  {
    "soort": {
      "code": "NTA",
      "naam": "Energielabel conform NTA8800"
    },
    "status": {
      "code": "DEF",
      "naam": "Definitief"
    },
    "begindatum": "2024-07-18",
    "einddatum": "2034-07-18",
    "registratiedatum": "2024-07-24T00:00:00.000000+01:00",
    "label": {
      "code": "A",
      "naam": "A"
    },
    "waarde": "80.17"
  }
]
```

---

## Monumenten

Array van Referentiedata. Leeg array `[]` als de woning geen monument is.

| Code | Naam |
|------|------|
| `RM` | Rijksmonument |
| `BSG` | Beschermd stadsgezicht |
| `GM` | Gemeentelijk monument |
| `PM` | Provinciaal monument |

```json
"monumenten": []
```

---

## Doelgroep

Optioneel. Bepaalt of bijzondere voorzieningen meetellen.

| Code | Naam |
|------|------|
| `ZOR` | Zorg |

```json
"doelgroep": {
  "code": "ZOR",
  "naam": "Zorg"
}
```

---

## Ruimten (`EenhedenRuimte[]`) - Kern van de berekening

Dit is het belangrijkste en meest gedetailleerde onderdeel. Elke ruimte in de woning wordt als apart object beschreven.

### Velden per ruimte

| Veld | Type | Verplicht | Beschrijving |
|------|------|-----------|-------------|
| `id` | `string` | Ja | Uniek ID van de ruimte |
| `naam` | `string` | Nee | Naam (bijv. "Woonkamer", "Slaapkamer") |
| `soort` | `Referentiedata` | Ja | Hoofdcategorie van de ruimte |
| `detailSoort` | `Referentiedata` | Ja | Specifiek type ruimte |
| `oppervlakte` | `float` | Ja | Vloeroppervlakte in m2 |
| `inhoud` | `float` | Nee | Volume in m3 |
| `lengte` | `float` | Nee* | Lengte in meters |
| `breedte` | `float` | Nee* | Breedte in meters |
| `hoogte` | `float` | Nee | Hoogte in meters |
| `verwarmd` | `boolean` | Ja | Is de ruimte verwarmd? |
| `verkoeld` | `boolean` | Nee | Is de ruimte gekoeld? |
| `afsluitbaar` | `boolean` | Nee | Is de ruimte afsluitbaar? |
| `gemeenschappelijk` | `boolean` | Nee | Gemeenschappelijke ruimte? |
| `gedeeldMetAantalEenheden` | `integer` | Nee | Aantal eenheden dat de ruimte deelt |
| `gedeeldMetAantalOnzelfstandigeWoonruimten` | `integer` | Nee** | Aantal onzelfstandige woonruimten dat deelt |
| `bouwkundigeElementen` | `BouwkundigElement[]` | Nee | Bouwkundige elementen in de ruimte |
| `installaties` | `Referentiedata[]` | Nee | Installaties (sanitair etc.) |
| `verbondenRuimten` | `EenhedenRuimte[]` | Nee | Ruimten die met deze ruimte verbonden zijn |
| `bouwlaag` | `object` | Nee | Verdieping waarop de ruimte zich bevindt |
| `aantal` | `integer` | Nee | Aantal identieke ruimten (default 1) |

*\* `lengte` en `breedte` zijn verplicht voor buitenruimten (BTR) voor de puntenberekening.*
*\*\* `gedeeldMetAantalOnzelfstandigeWoonruimten` is specifiek voor ONZ-stelsel.*

### Ruimtesoort codes (hoofdcategorie)

| Code | Naam | Beschrijving |
|------|------|-------------|
| `VTK` | Vertrek | Verblijfsruimte (woonkamer, slaapkamer, keuken, badkamer) |
| `VRK` | Verkeersruimte | Verkeer/circulatieruimte (hal, gang, overloop) |
| `OVR` | Overige ruimten | Overige ruimtes (berging, kast, toilet, technische ruimte) |
| `BTR` | Buitenruimte | Buitenruimte (balkon, tuin, terras) |

### Ruimte detailsoort codes

#### Vertrekken (VTK)

| Code | Naam |
|------|------|
| `WOO` | Woonkamer |
| `SLA` | Slaapkamer |
| `KEU` | Keuken |
| `BAD` | Badruimte |

#### Verkeersruimten (VRK)

| Code | Naam |
|------|------|
| `HAL` | Hal |
| `GAN` | Gang |
| `OVL` | Overloop |
| `TRA` | Trap |

#### Overige ruimten (OVR)

| Code | Naam |
|------|------|
| `BER` | Berging |
| `KAS` | Kast |
| `TOI` | Toiletruimte |
| `TEC` | Technische ruimte |
| `MET` | Meterruimte |
| `SCH` | Schacht |
| `OVR` | Overige ruimte |
| `WAS` | Wasruimte |
| `ZOL` | Zolder |
| `GAR` | Garage |

#### Buitenruimten (BTR)

| Code | Naam |
|------|------|
| `BAL` | Balkon |
| `TUI` | Tuin |
| `TER` | Terras |
| `DAK` | Dakterras |
| `LOG` | Loggia |
| `GAL` | Galerij |

### Bouwlaag

```json
"bouwlaag": {
  "nummer": "03",
  "omschrijving": "derde verdieping"
}
```

| Nummer | Omschrijving |
|--------|-------------|
| `00` | Begane grond |
| `01` | Eerste verdieping |
| `02` | Tweede verdieping |
| `03` | Derde verdieping |
| etc. | etc. |

---

## Bouwkundige Elementen (`BouwkundigElement[]`)

Elementen binnen een ruimte die relevant zijn voor de puntentelling (aanrecht, sanitair, verwarming).

| Veld | Type | Verplicht | Beschrijving |
|------|------|-----------|-------------|
| `id` | `string` | Ja | Uniek ID |
| `id_bimmodel` | `string` | Nee | BIM-model referentie |
| `naam` | `string` | Nee | Naam (bijv. "Aanrecht", "Douche") |
| `omschrijving` | `string` | Nee | Nadere omschrijving |
| `soort` | `Referentiedata` | Ja | Hoofdcategorie |
| `detailSoort` | `Referentiedata` | Ja | Specifiek type |
| `lengte` | `integer` | Nee* | Lengte in millimeters |
| `begindatum` | `string` (date) | Nee | Datum installatie |
| `extraAttributen` | `object` | Nee | Vrije key-value attributen |

*\* `lengte` is verplicht voor aanrechten (code `AAN`). De waarde is in **millimeters**.*

### Bouwkundig element soort codes

| Code | Naam | Beschrijving |
|------|------|-------------|
| `SAN` | Sanitaire voorziening | Douche, bad, wastafel, toilet |
| `KEU` | Keuken voorziening | Aanrecht |
| `VER` | Verwarming | Ketel, radiator |
| `VOO` | Voorziening algemeen | Algemene voorzieningen |

### Bouwkundig element detailsoort codes

#### Sanitair (SAN)

| Code | Naam |
|------|------|
| `DOU` | Douche |
| `BAD` | Bad |
| `WAS` | Wastafel/Fontein |
| `CLO` | Toilet |

#### Keuken (KEU)

| Code | Naam |
|------|------|
| `AAN` | Aanrecht |

#### Verwarming (VER)

| Code | Naam |
|------|------|
| `VTO` | Verwarmingstoestellen |
| `RAD` | Radiator |

### Voorbeeld: Aanrecht (let op: lengte in mm)

```json
{
  "id": "Aanrecht_82123576",
  "naam": "Aanrecht",
  "soort": {
    "code": "KEU",
    "naam": "Keuken voorziening"
  },
  "detailSoort": {
    "code": "AAN",
    "naam": "Aanrecht"
  },
  "lengte": 2100
}
```

### Voorbeeld: Douche

```json
{
  "id": "Douche_82123432",
  "naam": "Douche",
  "soort": {
    "code": "SAN",
    "naam": "Sanitaire voorziening"
  },
  "detailSoort": {
    "code": "DOU",
    "naam": "Douche"
  }
}
```

### Voorbeeld: Toilet

```json
{
  "id": "Closetcombinatie_82123500",
  "naam": "Closetcombinatie",
  "soort": {
    "code": "SAN",
    "naam": "Sanitaire voorziening"
  },
  "detailSoort": {
    "code": "CLO",
    "naam": "Toilet"
  }
}
```

---

## Installaties (alternatief voor bouwkundige elementen)

Sommige ruimten gebruiken `installaties` in plaats van `bouwkundigeElementen` voor sanitaire voorzieningen. Dit is een vereenvoudigde notatie als Referentiedata-array.

| Code | Naam |
|------|------|
| `STO` | Staand toilet |
| `DOU` | Douche |
| `BAD` | Bad |
| `WAS` | Wastafel |

```json
"installaties": [
  {
    "code": "STO",
    "naam": "Staand toilet"
  }
]
```

---

## Verbonden Ruimten (`verbondenRuimten`)

Een ruimte kan `verbondenRuimten` bevatten: ruimten die fysiek verbonden zijn (bijv. een kast die uitkomt op een keuken). Dit is een geneste array van hetzelfde `EenhedenRuimte`-type. Verbonden ruimten zijn relevant voor de oppervlakteberekening van vertrekken.

```json
{
  "id": "Space_keuken",
  "naam": "Keuken",
  "soort": { "code": "VTK" },
  "detailSoort": { "code": "KEU" },
  "oppervlakte": 9.5,
  "verbondenRuimten": [
    {
      "id": "Space_kast1",
      "soort": { "code": "OVR" },
      "detailSoort": { "code": "KAS" },
      "naam": "Kast",
      "oppervlakte": 0.31,
      "verwarmd": false,
      "afsluitbaar": false
    }
  ]
}
```

---

## Gedeelde ruimten (Onzelfstandige woonruimten)

Bij onzelfstandige woonruimten (stelsel `ONZ`) worden ruimten vaak gedeeld met andere bewoners. Dit wordt aangegeven met:

| Veld | Beschrijving |
|------|-------------|
| `gedeeldMetAantalOnzelfstandigeWoonruimten` | Aantal onzelfstandige eenheden dat deze ruimte deelt |
| `gedeeldMetAantalEenheden` | Totaal aantal eenheden dat deze ruimte deelt |

```json
{
  "id": "Space_keuken",
  "naam": "Keuken",
  "soort": { "code": "VTK" },
  "detailSoort": { "code": "KEU" },
  "oppervlakte": 7.5,
  "verwarmd": false,
  "gedeeldMetAantalOnzelfstandigeWoonruimten": 2
}
```

---

## Stelselgroepen (berekeningsonderdelen)

De calculator evalueert de volgende groepen in volgorde. Elk onderdeel levert punten op.

### Zelfstandige woonruimten (ZEL)

| Groep | Beschrijving | Relevante input |
|-------|-------------|-----------------|
| Oppervlakte van vertrekken | m2 van VTK-ruimten | `ruimten` met `soort.code = "VTK"` |
| Oppervlakte van overige ruimten | m2 van OVR-ruimten | `ruimten` met `soort.code = "OVR"` |
| Verkoeling en verwarming | Verwarmde/gekoelde ruimten | `verwarmd`, `verkoeld`, `klimaatbeheersing` |
| Buitenruimten | Balkons, tuinen etc. | `ruimten` met `soort.code = "BTR"` |
| Energieprestatie | Energielabel | `energieprestaties` |
| Keuken | Aanrechtlengte | `bouwkundigeElementen` met `detailSoort.code = "AAN"` |
| Sanitair | Douche, bad, toilet, wastafel | `bouwkundigeElementen`/`installaties` met SAN-codes |
| Gemeenschappelijke parkeerruimten | Parkeerplekken | `ruimten` met parkeerruimte-codes |
| Gemeenschappelijke ruimten | Gedeelde vertrekken/overige | `gemeenschappelijk = true` |
| Punten voor de WOZ-waarde | WOZ-waarde | `wozEenheden` |
| Bijzondere voorzieningen | Zorgwoning extra's | `doelgroep` |
| Prijsopslag monumenten | Monumentstatus | `monumenten` |

### Onzelfstandige woonruimten (ONZ)

Vergelijkbare groepen, maar met aanvullend:
- **Aftrekpunten**: Correctie voor gedeelde voorzieningen
- **Gemeenschappelijke binnenruimten**: Gedeeld met meerdere adressen

---

## Volledig voorbeeld: Zelfstandige woonruimte

```json
{
  "id": "12006000004",
  "bouwjaar": 1981,
  "woningwaarderingstelsel": {
    "code": "ZEL",
    "naam": "Zelfstandige woonruimte"
  },
  "klimaatbeheersing": [
    { "code": "IND", "naam": "Individueel" }
  ],
  "adres": {
    "straatnaam": "Voorbeeldstraat",
    "huisnummer": "10",
    "postcode": "3011AB",
    "woonplaats": { "naam": "ROTTERDAM" }
  },
  "panden": [
    { "soort": { "code": "MGW", "naam": "Meergezinswoning" } }
  ],
  "wozEenheden": [
    { "waardepeildatum": "2024-01-01", "vastgesteldeWaarde": 318000 }
  ],
  "energieprestaties": [
    {
      "soort": { "code": "NTA", "naam": "Energielabel conform NTA8800" },
      "status": { "code": "DEF", "naam": "Definitief" },
      "begindatum": "2024-07-18",
      "einddatum": "2034-07-18",
      "label": { "code": "A", "naam": "A" },
      "waarde": "80.17"
    }
  ],
  "gebruiksoppervlakte": 71,
  "monumenten": [],
  "ruimten": [
    {
      "id": "woonkamer_1",
      "soort": { "code": "VTK", "naam": "Vertrek" },
      "detailSoort": { "code": "WOO", "naam": "Woonkamer" },
      "naam": "Woonkamer",
      "oppervlakte": 25.96,
      "inhoud": 67.5,
      "verwarmd": true,
      "afsluitbaar": true
    },
    {
      "id": "keuken_1",
      "soort": { "code": "VTK", "naam": "Vertrek" },
      "detailSoort": { "code": "KEU", "naam": "Keuken" },
      "naam": "Keuken",
      "oppervlakte": 9.56,
      "inhoud": 24.85,
      "verwarmd": true,
      "afsluitbaar": true,
      "bouwkundigeElementen": [
        {
          "id": "aanrecht_1",
          "naam": "Aanrecht",
          "soort": { "code": "KEU", "naam": "Keuken voorziening" },
          "detailSoort": { "code": "AAN", "naam": "Aanrecht" },
          "lengte": 2100
        }
      ]
    },
    {
      "id": "slaapkamer_1",
      "soort": { "code": "VTK", "naam": "Vertrek" },
      "detailSoort": { "code": "SLA", "naam": "Slaapkamer" },
      "naam": "Slaapkamer",
      "oppervlakte": 12.98,
      "verwarmd": true
    },
    {
      "id": "badkamer_1",
      "soort": { "code": "VTK", "naam": "Vertrek" },
      "detailSoort": { "code": "BAD", "naam": "Badruimte" },
      "naam": "Badruimte",
      "oppervlakte": 3.58,
      "verwarmd": true,
      "bouwkundigeElementen": [
        {
          "id": "douche_1",
          "naam": "Douche",
          "soort": { "code": "SAN", "naam": "Sanitaire voorziening" },
          "detailSoort": { "code": "DOU", "naam": "Douche" }
        },
        {
          "id": "wastafel_1",
          "naam": "Wastafel",
          "soort": { "code": "SAN", "naam": "Sanitaire voorziening" },
          "detailSoort": { "code": "WAS", "naam": "Wastafel/Fontein" }
        }
      ]
    },
    {
      "id": "toilet_1",
      "soort": { "code": "OVR", "naam": "Overige ruimtes" },
      "detailSoort": { "code": "TOI", "naam": "Toiletruimte" },
      "naam": "Toiletruimte",
      "oppervlakte": 1.26,
      "verwarmd": false,
      "bouwkundigeElementen": [
        {
          "id": "wc_1",
          "naam": "Closetcombinatie",
          "soort": { "code": "SAN", "naam": "Sanitaire voorziening" },
          "detailSoort": { "code": "CLO", "naam": "Toilet" }
        },
        {
          "id": "fontein_1",
          "soort": { "code": "SAN", "naam": "Sanitaire voorziening" },
          "detailSoort": { "code": "WAS", "naam": "Wastafel/Fontein" }
        }
      ]
    },
    {
      "id": "hal_1",
      "soort": { "code": "VRK", "naam": "Verkeersruimte" },
      "detailSoort": { "code": "HAL", "naam": "Hal" },
      "naam": "Hal",
      "oppervlakte": 6.2,
      "verwarmd": true,
      "afsluitbaar": true
    },
    {
      "id": "balkon_1",
      "soort": { "code": "BTR", "naam": "Buitenruimte" },
      "detailSoort": { "code": "BAL", "naam": "Balkon" },
      "naam": "Balkon",
      "oppervlakte": 1.82,
      "lengte": 1.29,
      "breedte": 1.5,
      "hoogte": 2.6,
      "verwarmd": false
    }
  ]
}
```

---

## Volledig voorbeeld: Onzelfstandige woonruimte

```json
{
  "id": "15004000185",
  "bouwjaar": 1998,
  "woningwaarderingstelsel": {
    "code": "ONZ",
    "naam": "Onzelfstandige woonruimten"
  },
  "adres": {
    "huisnummer": "5",
    "postcode": "3086XX",
    "straatnaam": "Voorbeeldlaan",
    "woonplaats": { "code": "3086", "naam": "ROTTERDAM" }
  },
  "panden": [
    { "soort": { "code": "MGW", "naam": "Meergezinswoning" } }
  ],
  "wozEenheden": [
    { "waardepeildatum": "2024-01-01", "vastgesteldeWaarde": 205000 }
  ],
  "energieprestaties": [],
  "monumenten": [],
  "ruimten": [
    {
      "id": "slaapkamer_1",
      "soort": { "code": "VTK", "naam": "Vertrek" },
      "detailSoort": { "code": "SLA", "naam": "Slaapkamer" },
      "naam": "Slaapkamer",
      "oppervlakte": 20.04,
      "verwarmd": true,
      "bouwkundigeElementen": [
        {
          "id": "rad_1",
          "naam": "Radiator",
          "soort": { "code": "VOO", "naam": "Voorziening algemeen" },
          "detailSoort": { "code": "RAD", "naam": "Radiator" }
        }
      ]
    },
    {
      "id": "keuken_1",
      "soort": { "code": "VTK", "naam": "Vertrek" },
      "detailSoort": { "code": "KEU", "naam": "Keuken" },
      "naam": "Keuken",
      "oppervlakte": 7.5,
      "verwarmd": false,
      "gedeeldMetAantalOnzelfstandigeWoonruimten": 2,
      "bouwkundigeElementen": [
        {
          "id": "aanrecht_1",
          "naam": "Aanrecht",
          "soort": { "code": "KEU", "naam": "Keuken voorziening" },
          "detailSoort": { "code": "AAN", "naam": "Aanrecht" },
          "lengte": 2220
        }
      ]
    },
    {
      "id": "toilet_1",
      "soort": { "code": "OVR", "naam": "Overige ruimten" },
      "detailSoort": { "code": "TOI", "naam": "Toilet" },
      "naam": "Toilet",
      "oppervlakte": 1.0,
      "verwarmd": false,
      "gedeeldMetAantalOnzelfstandigeWoonruimten": 2,
      "installaties": [
        { "code": "STO", "naam": "Staand toilet" }
      ]
    },
    {
      "id": "badkamer_1",
      "soort": { "code": "VTK", "naam": "Vertrek" },
      "detailSoort": { "code": "BAD", "naam": "Badruimte" },
      "naam": "Badruimte",
      "oppervlakte": 1.7,
      "verwarmd": false,
      "gedeeldMetAantalOnzelfstandigeWoonruimten": 2,
      "installaties": [
        { "code": "DOU", "naam": "Douche" }
      ]
    }
  ]
}
```

---

## Opmerkingen

- **JSON veldnamen**: De modellen ondersteunen zowel `camelCase` als `snake_case` (bijv. zowel `detailSoort` als `detail_soort`). De voorbeelden in de testdata gebruiken overwegend `camelCase`.
- **Aanrecht lengte**: Altijd in **millimeters** (bijv. `2100` = 2.1 meter).
- **Oppervlakten**: Altijd in **vierkante meters** (m2).
- **Volumes**: Altijd in **kubieke meters** (m3).
- **Afmetingen (lengte/breedte/hoogte bij ruimten)**: In **meters**.
- **Datums**: ISO 8601 formaat (`YYYY-MM-DD` of met tijdzone).
- **WOZ-waarden**: In hele euro's.
- **Lege arrays**: Gebruik `[]` voor velden zonder data (bijv. `"monumenten": []`).
