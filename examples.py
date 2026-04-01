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


# Better example with missing elements to trigger improvement suggestions
OPTIMIZATION_READY = {
    "eenheid_data": {
        "id": "opt_unit_001",
        "bouwjaar": 1975,
        "gebruiksoppervlakte": 120,
        "woningwaarderingstelsel": {"code": "ZEL"},
        "adres": {
            "straatnaam": "Optimalisatielaan",
            "huisnummer": "42",
            "postcode": "5678CD",
            "woonplaats": {"naam": "Utrecht"}
        },
        "panden": [
            {
                "soort": {"code": "EGW"}
            }
        ],
        "ruimten": [
            {
                "id": "bedroom_1",
                "soort": {"code": "VTK"},
                "detail_soort": {"code": "SLA"},
                "naam": "Master Bedroom",
                "oppervlakte": 20,
                "inhoud": 50,
                "verwarmd": True
            },
            {
                "id": "bedroom_2",
                "soort": {"code": "VTK"},
                "detail_soort": {"code": "SLA"},
                "naam": "Second Bedroom",
                "oppervlakte": 12,
                "inhoud": 30,
                "verwarmd": False  # Unheated room - can suggest heating
            },
            {
                "id": "kitchen_1",
                "soort": {"code": "VTK"},
                "detail_soort": {"code": "KEU"},
                "naam": "Kitchen",
                "oppervlakte": 12,
                "inhoud": 30,
                "verwarmd": True,
                "bouwkundige_elementen": [
                    {
                        "id": "elem_aanrecht_1",
                        "naam": "Aanrecht",
                        "soort": {"code": "VOO"},
                        "detail_soort": {"code": "AAN"},
                        "lengte": 1200
                    }
                    # Missing: Spoelbak (sink) - can suggest adding
                    # Missing: Kast (cupboard) - can suggest adding
                ]
            },
            {
                "id": "bathroom_1",
                "soort": {"code": "VTK"},
                "detail_soort": {"code": "BAD"},
                "naam": "Bathroom",
                "oppervlakte": 6,
                "inhoud": 15,
                "verwarmd": True,
                "bouwkundige_elementen": [
                    {
                        "id": "elem_bad_1",
                        "naam": "Bad",
                        "soort": {"code": "VOO"},
                        "detail_soort": {"code": "BAD"},
                        "lengte": 1600
                    }
                    # Missing: Douchebak (shower) - can suggest adding
                    # Missing: Toilet - can suggest adding
                ]
            },
            {
                "id": "living_1",
                "soort": {"code": "VTK"},
                "detail_soort": {"code": "WON"},
                "naam": "Living Room",
                "oppervlakte": 25,
                "inhoud": 62.5,
                "verwarmd": True
            },
            {
                "id": "hallway_1",
                "soort": {"code": "VTK"},
                "detail_soort": {"code": "OVE"},
                "naam": "Hallway",
                "oppervlakte": 8,
                "inhoud": 20,
                "verwarmd": False  # Unheated hallway - can suggest heating
            }
        ],
        "energieprestaties": [
            {
                "soort": {"code": "EI"},
                "status": {"code": "DEFINITIEF"},
                "begindatum": "2019-02-25",
                "einddatum": "2029-02-25",
                "registratiedatum": "2019-02-26T14:51:38+01:00",
                "label": {"code": "D"},  # Lower energy label - can suggest improvement
                "waarde": "2.15"
            }
        ],
        "woz_eenheden": [
            {
                "waardepeildatum": "2024-01-01",
                "vastgestelde_waarde": 420000
            }
        ],
        "monumenten": []
    },
    "peildatum": str(date.today())
}

# Real-world example from actual VERA data
REAL_WORLD = {
    "eenheid_data": {
        "id": "3004649",
        "woningwaarderingstelsel": {"code": "ZEL"},
        "ruimten": [
            {
                "id": "0.07.355",
                "naam": "slaapkamer 2",
                "soort": {"code": "VTK"},
                "detail_soort": {"code": "SLA"},
                "oppervlakte": 5.97,
                "verwarmd": True,
                "inhoud": 14.57,
                "hoogte": 2.44,
                "afsluitbaar": True
            },
            {
                "id": "0.07.356",
                "naam": "slaapkamer 1",
                "soort": {"code": "VTK"},
                "detail_soort": {"code": "SLA"},
                "oppervlakte": 11.16,
                "verwarmd": True,
                "inhoud": 27.2,
                "hoogte": 2.44,
                "afsluitbaar": True
            },
            {
                "id": "0.07.357",
                "naam": "hal",
                "soort": {"code": "VRK"},
                "detail_soort": {"code": "HAL"},
                "oppervlakte": 6.97,
                "verwarmd": True,
                "inhoud": 17.0,
                "hoogte": 2.44,
                "afsluitbaar": False
            },
            {
                "id": "0.07.358",
                "naam": "MK warm",
                "soort": {"code": "OVR"},
                "detail_soort": {"code": "MET"},
                "oppervlakte": 0.28,
                "verwarmd": False,
                "inhoud": 0.69,
                "hoogte": 2.44,
                "afsluitbaar": False
            },
            {
                "id": "0.07.359",
                "naam": "MK koud",
                "soort": {"code": "OVR"},
                "detail_soort": {"code": "MET"},
                "oppervlakte": 0.28,
                "verwarmd": False,
                "inhoud": 0.69,
                "hoogte": 2.44,
                "afsluitbaar": False
            },
            {
                "id": "0.07.360",
                "naam": "berging/techniek",
                "soort": {"code": "OVR"},
                "detail_soort": {"code": "BER"},
                "oppervlakte": 4.54,
                "verwarmd": False,
                "inhoud": 11.06,
                "hoogte": 2.44,
                "afsluitbaar": False
            },
            {
                "id": "0.07.361",
                "naam": "woonkamer / keuken",
                "soort": {"code": "VTK"},
                "detail_soort": {"code": "WOO"},
                "oppervlakte": 27.0,
                "verwarmd": True,
                "inhoud": 65.84,
                "hoogte": 2.44,
                "afsluitbaar": True,
                "bouwkundige_elementen": [
                    {
                        "id": "0.07.361_AAN",
                        "naam": "Aanrecht",
                        "soort": {"code": "VOO"},
                        "detail_soort": {"code": "AAN"},
                        "lengte": 2100
                    }
                ]
            },
            {
                "id": "0.07.362",
                "naam": "badkamer/toilet",
                "soort": {"code": "VTK"},
                "detail_soort": {"code": "BAD"},
                "oppervlakte": 6.04,
                "verwarmd": True,
                "inhoud": 14.73,
                "hoogte": 2.44,
                "afsluitbaar": True,
                "bouwkundige_elementen": [
                    {
                        "id": "0.07.362_DOU",
                        "naam": "Douche",
                        "soort": {"code": "VOO"},
                        "detail_soort": {"code": "DOU"},
                        "lengte": 800
                    },
                    {
                        "id": "0.07.362_WAS",
                        "naam": "Wastafel",
                        "soort": {"code": "VOO"},
                        "detail_soort": {"code": "WAS"},
                        "lengte": 600
                    },
                    {
                        "id": "0.07.362_CLO",
                        "naam": "Toilet",
                        "soort": {"code": "VOO"},
                        "detail_soort": {"code": "CLO"},
                        "lengte": 600
                    }
                ]
            }
        ],
        "adres": {
            "straatnaam": "Fascinatio Boulevard",
            "huisnummer": "1524",
            "postcode": "2909 VD",
            "woonplaats": {"naam": "CAPELLE AAN DEN IJSSEL"}
        },
        "panden": [
            {
                "soort": {"code": "MGW"}
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

    # Test with real-world example
    print("=" * 60)
    print("Testing with Real-World Example (ID: 3004649)")
    print("=" * 60 + "\n")

    # Calculate
    print("2. Calculate Score")
    r = requests.post(f"{API_URL}/calculate", json=REAL_WORLD)
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
    r = requests.post(f"{API_URL}/optimize", json=REAL_WORLD)
    result = r.json()

    if "error" in result or "detail" in result:
        print(f"   ❌ Error: {result.get('detail', result.get('error', 'Unknown'))}\n")
    else:
        print(f"   ✓ Unit ID: {result.get('eenheid_id', 'N/A')}")
        count = result.get("suggestion_count", 0)
        print(f"   ✓ Found {count} improvement suggestions")

        if count > 0:
            for i, sugg in enumerate(result["suggestions"][:5], 1):
                print(f"     {i}. {sugg.get('title')} (+{sugg.get('estimated_score_gain', 0):.1f})")
        print()

    print("✨ Examples completed!\n")


if __name__ == "__main__":
    main()