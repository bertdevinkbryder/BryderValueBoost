"""
Tests for the Woningwaardering API.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import date
from main import app

client = TestClient(app)


def test_health_check():
    """Test that the health check endpoint works."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_calculate_basic_unit():
    """Test calculating woning waarde for a basic housing unit."""
    
    # Use proper VERA referentiedata format
    request_data = {
        "eenheid_data": {
            "id": "test_001",
            "bouwjaar": 1975,
            "gebruiksoppervlakte": 100,
            "woningwaarderingstelsel": {
                "code": "ZEL"
            },
            "adres": {
                "straatnaam": "Testlaan",
                "huisnummer": "1",
                "postcode": "1234AB",
                "woonplaats": {"naam": "Rotterdam"}
            },
            "ruimten": [
                {
                    "id": "room_1",
                    "soort": {
                        "code": "VT"
                    },
                    "detail_soort": {
                        "code": "SK"
                    },
                    "naam": "Main Bedroom",
                    "oppervlakte": 20,
                    "inhoud": 50,
                    "verwarmd": True
                }
            ]
        },
        "peildatum": "2026-03-26"
    }
    
    response = client.post("/calculate", json=request_data)
    assert response.status_code == 200
    
    result = response.json()
    assert result["success"] is True
    assert result["eenheid_id"] == "test_001"
    assert result["detailed_json"] is not None
    assert result["table_output"] is not None


def test_calculate_with_multiple_rooms():
    """Test calculating for a more complex unit."""
    
    request_data = {
        "eenheid_data": {
            "id": "complex_001",
            "bouwjaar": 2000,
            "gebruiksoppervlakte": 150,
            "woningwaarderingstelsel": {
                "code": "ZEL"
            },
            "adres": {
                "straatnaam": "Complexlaan",
                "huisnummer": "42",
                "postcode": "5678CD",
                "woonplaats": {"naam": "Utrecht"}
            },
            "ruimten": [
                {
                    "id": "room_1",
                    "soort": {
                        "code": "VT"
                    },
                    "detail_soort": {
                        "code": "SK"
                    },
                    "naam": "Master Bedroom",
                    "oppervlakte": 20,
                    "inhoud": 50,
                    "verwarmd": True
                },
                {
                    "id": "room_2",
                    "soort": {
                        "code": "VT"
                    },
                    "detail_soort": {
                        "code": "SK"
                    },
                    "naam": "Second Bedroom",
                    "oppervlakte": 15,
                    "inhoud": 37.5,
                    "verwarmd": True
                },
                {
                    "id": "room_3",
                    "soort": {
                        "code": "VT"
                    },
                    "detail_soort": {
                        "code": "KK"
                    },
                    "naam": "Kitchen",
                    "oppervlakte": 15,
                    "inhoud": 37.5,
                    "verwarmd": True
                },
                {
                    "id": "room_4",
                    "soort": {
                        "code": "VT"
                    },
                    "detail_soort": {
                        "code": "BK"
                    },
                    "naam": "Bathroom",
                    "oppervlakte": 5,
                    "inhoud": 12.5,
                    "verwarmd": True
                }
            ]
        }
    }
    
    response = client.post("/calculate", json=request_data)
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True


def test_calculate_invalid_input():
    """Test that invalid input returns proper error."""
    
    request_data = {
        "eenheid_data": {
            # Missing required fields
            "id": "invalid"
        }
    }
    
    response = client.post("/calculate", json=request_data)
    assert response.status_code in [422, 500]  # Validation or processing error


def test_optimize_suggestions():
    """Test that optimization endpoint provides suggestions."""
    
    request_data = {
        "eenheid_data": {
            "id": "optimize_001",
            "bouwjaar": 1950,
            "gebruiksoppervlakte": 80,
            "woningwaarderingstelsel": {
                "code": "ZEL"
            },
            "adres": {
                "straatnaam": "Optimizationstraat",
                "huisnummer": "10",
                "postcode": "9999ZZ",
                "woonplaats": {"naam": "Amsterdam"}
            },
            "ruimten": [
                {
                    "id": "room_1",
                    "soort": {
                        "code": "VT"
                    },
                    "detail_soort": {
                        "code": "SK"
                    },
                    "naam": "Bedroom",
                    "oppervlakte": 15,
                    "inhoud": 37.5,
                    "verwarmd": True
                }
            ]
        }
    }
    
    response = client.post("/optimize", json=request_data)
    assert response.status_code == 200
    
    result = response.json()
    assert result["success"] is True
    assert "suggestions" in result
    assert isinstance(result["suggestions"], list)
    
    # Check suggestion structure
    if len(result["suggestions"]) > 0:
        suggestion = result["suggestions"][0]
        assert "category" in suggestion
        assert "title" in suggestion
        assert "estimated_score_gain" in suggestion


def test_batch_calculate():
    """Test batch calculation."""
    
    request_data = [
        {
            "eenheid_data": {
                "id": "batch_001",
                "bouwjaar": 1980,
                "gebruiksoppervlakte": 90,
                "woningwaarderingstelsel": {
                    "code": "ZEL"
                },
                "adres": {
                    "straatnaam": "Batchstraat",
                    "huisnummer": "1",
                    "postcode": "1111AA",
                    "woonplaats": {"naam": "Rotterdam"}
                },
                "ruimten": [{
                    "id": "r1",
                    "soort": {
                        "code": "VT"
                    },
                    "detail_soort": {
                        "code": "SK"
                    },
                    "naam": "Bedroom",
                    "oppervlakte": 15,
                    "inhoud": 37.5,
                    "verwarmd": True
                }]
            }
        },
        {
            "eenheid_data": {
                "id": "batch_002",
                "bouwjaar": 1990,
                "gebruiksoppervlakte": 110,
                "woningwaarderingstelsel": {
                    "code": "ZEL"
                },
                "adres": {
                    "straatnaam": "Batchstraat",
                    "huisnummer": "2",
                    "postcode": "1111AA",
                    "woonplaats": {"naam": "Rotterdam"}
                },
                "ruimten": [{
                    "id": "r2",
                    "soort": {
                        "code": "VT"
                    },
                    "detail_soort": {
                        "code": "SK"
                    },
                    "naam": "Bedroom",
                    "oppervlakte": 18,
                    "inhoud": 45,
                    "verwarmd": True
                }]
            }
        }
    ]
    
    response = client.post("/batch-calculate", json=request_data)
    assert response.status_code == 200
    
    result = response.json()
    assert result["total"] == 2
    assert result["successful"] >= 0
    assert "results" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
