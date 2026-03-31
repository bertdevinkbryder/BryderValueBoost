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

API_URL = "http://localhost:8000"

SIMPLE = {
    "eenheid_data": {
        "id": "example_001",
        "bouwjaar": 1924,
        "woningwaarderingstelsel": {"code": "ZEL"},
        "adres": {
            "straatnaam": "Examplestraat",
            "huisnummer": "1",
            "huisnummer_toevoeging": "",
            "postcode": "3012AB",
            "woonplaats": {"naam": "Rotterdam"}
        },
        "adresseerbaar_object_basisregistratie": {
            "id": "0599010000485697",
            "bag_identificatie": "0599010000485697"
        },
        
        "panden": [
            {
                "soort": {"code": "EGW"}   # Eengezinswoning
            }
        ],


        "woz_eenheden": [
            {
                "waardepeildatum": "2024-01-01",
                "vastgestelde_waarde": 694000
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

        "gebruiksoppervlakte": 187,
        "monumenten": [],

        "ruimten": [
            {
                "id": "room_bedroom_1",
                "soort": {"code": "VT"},
                "detail_soort": {"code": "SK"},
                "naam": "Slaapkamer",
                "inhoud": 60.4,
                "oppervlakte": 21.0,
                "verwarmd": True
            },
            {
                "id": "room_kitchen_1",
                "soort": {"code": "VT"},
                "detail_soort": {"code": "KK"},
                "naam": "Keuken",
                "inhoud": 57.4,
                "oppervlakte": 20.4,
                "verwarmd": True,
                "bouwkundige_elementen": [
                    {
                        "id": "elem_001",
                        "naam": "Aanrecht",
                        "omschrijving": "Aanrecht in Keuken",
                        "soort": {"code": "VOORZIENING"},
                        "detail_soort": {"code": "AANRECHT"},
                        "lengte": 2700
                    }
                ]
            }
        ]
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