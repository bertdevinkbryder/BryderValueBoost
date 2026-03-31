"""Example API usage - run with: python examples.py"""
import requests
from datetime import date
from woningwaardering.vera.bvg.generated import (
    BouwkundigElementenBouwkundigElement,
    EenhedenAdresseerbaarObjectBasisregistratie,
    EenhedenEenheid,
    EenhedenEenheidadres,
    EenhedenEnergieprestatie,
    EenhedenPand,
    EenhedenRuimte,
    EenhedenWoonplaats,
    EenhedenWozEenheid,
)
from woningwaardering.vera.referentiedata import (
    Bouwkundigelementdetailsoort,
    Bouwkundigelementsoort,
    Energielabel,
    Energieprestatiesoort,
    Energieprestatiestatus,
    Pandsoort,
    Ruimtedetailsoort,
    Ruimtesoort,
    Woningwaarderingstelsel,
)


# print(list(Bouwkundigelementsoort))
# print(list(Bouwkundigelementdetailsoort))
API_URL = "http://localhost:8000"

SIMPLE = {
"eenheid_data": {
    "id": "test_unit_001",
    "bouwjaar": 1980,
    "gebruiksoppervlakte": 100,
    "woningwaarderingstelsel": {"code": "ZEL"},
    "adres": {
        "straatnaam": "Teststraat",
        "huisnummer": "1",
        "postcode": "1234AB",
        "woonplaats": {"naam": "Amsterdam"}
    },
    "panden": [
        {
            "soort": { "code": "EGW" }
        }
    ],
    "ruimten": [
        {
            "id": "bedroom_1",
            "soort": { "code": "VTK" },
            "detail_soort": { "code": "SLA" },
            "naam": "Slaapkamer",
            "oppervlakte": 15,
            "inhoud": 37.5,
            "verwarmd": True
        },
        {
            "id": "kitchen_1",
            "soort": { "code": "VTK" },
            "detail_soort": { "code": "KEU" },
            "naam": "Keuken",
            "oppervlakte": 10,
            "inhoud": 25,
            "verwarmd": True,
            "bouwkundige_elementen": [
                {
                    "id": "elem_aanrecht_1",
                    "naam": "Aanrecht",
                    "omschrijving": "Aanrecht in keuken",
                    "soort": { "code": "VOZ" },
                    "detail_soort": { "code": "AAN" },
                    "lengte": 1500
                }
            ]
        }
    ,
        {
            "id": "bathroom_1",
            "soort": { "code": "VTK" },
            "detail_soort": { "code": "BAD" },
            "naam": "Badkamer",
            "oppervlakte": 5,
            "inhoud": 12.5,
            "verwarmd": True
        }
    ],
    "energieprestaties": [
        {
            "soort": {"code": "EI"},
            "status": {"code": "DEFINITIEF"},
            "begindatum": "2019-02-25",
            "einddatum": "2029-02-25",
            "registratiedatum": "2019-02-26T14:51:38+01:00",
            "label": {"code": "C"},
            "waarde": "1.58"
        }
    ],
    "woz_eenheden": [
        {
            "waardepeildatum": "2024-01-01",
            "vastgestelde_waarde": 350000
        }
    ],
    "monumenten": []
},

    "peildatum": str(date.today())
}


def main():
    print("\n=== Woningwaardering API Examples ===\n")

    # Health check
    try:
        requests.get(f"{API_URL}/health", timeout=1)
    except Exception:
        print("❌ ERROR: API not running!")
        print("Start the API with: python main.py\n")
        return

    print("✓ 1. Health Check")
    r = requests.get(f"{API_URL}/health")
    print(f"   Status: {r.status_code}\n")

    # Calculate
    print("2. Calculate Score")
    r = requests.post(f"{API_URL}/calculate", json=SIMPLE)
    result = r.json()

    if "error" in result or "detail" in result:
        print(f"   ❌ Error: {result.get('detail', result.get('error', 'Unknown'))}\n")
    else:
        print(f"   ✓ Unit ID: {result.get('eenheid_id', 'N/A')}")
        print("   ✓ Calculation successful!")
        score_str = str(result.get("detailed_json", ""))[:100]
        print(f"   ✓ Score snippet: {score_str}...\n")

    # Optimize
    print("3. Find Improvements")
    r = requests.post(f"{API_URL}/optimize", json=SIMPLE)
    result = r.json()

    if "error" in result or "detail" in result:
        print(f"   ❌ Error: {result.get('detail', result.get('error', 'Unknown'))}\n")
    else:
        print(f"   ✓ Unit ID: {result.get('eenheid_id', 'N/A')}")
        count = result.get("suggestion_count", 0)
        print(f"   ✓ Found {count} improvement suggestions")

        if count > 0:
            for i, sugg in enumerate(result["suggestions"][:3], 1):
                print(f"     {i}. {sugg.get('title')} (+{sugg.get('estimated_score_gain', 0):.1f})")

    print("\n✨ Examples completed!\n")


if __name__ == "__main__":
    main()