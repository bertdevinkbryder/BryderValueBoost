"""Example API usage - run with: python examples.py"""
import requests
import json
from datetime import date

API_URL = "http://localhost:8000"

SIMPLE = {
    "eenheid_data": {
        "id": "example_001",
        "bouwjaar": 1975,
        "gebruiksoppervlakte": 100,
        "woningwaarderingstelsel": {"code": "ZEL"},
        "adres": {
            "straatnaam": "Straat",
            "huisnummer": "1",
            "postcode": "1234AB",
            "woonplaats": {"naam": "Rotterdam"}
        },
        "ruimten": [{
            "id": "room_1",
            "soort": {"code": "VT"},
            "detail_soort": {"code": "SK"},
            "naam": "Bedroom",
            "oppervlakte": 20,
            "inhoud": 50,
            "verwarmd": True
        }]
    },
    "peildatum": str(date.today())
}

def main():
    print("\n=== Woningwaardering API Examples ===\n")
    
    try:
        requests.get(f"{API_URL}/health", timeout=1)
    except:
        print("ERROR: API not running. Start with: python main.py")
        return
    
    print("1. Health Check")
    r = requests.get(f"{API_URL}/health")
    print(f"   Status: {r.status_code}\n")
    
    print("2. Calculate Score")
    r = requests.post(f"{API_URL}/calculate", json=SIMPLE)
    result = r.json()
    print(f"   Unit: {result['eenheid_id']}")
    print(f"   Score: {result['detailed_json'][:50]}...\n")
    
    print("3. Find Improvements")
    r = requests.post(f"{API_URL}/optimize", json=SIMPLE)
    result = r.json()
    print(f"   Found {result['suggestion_count']} suggestions\n")
    
    print(" Examples completed!\n")

if __name__ == "__main__":
    main()
