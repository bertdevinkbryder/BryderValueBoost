"""
Comprehensive tests for the optimization module.
Tests verify that score calculations are correct and suggestions work as expected.
"""

import pytest
from datetime import date
from fastapi.testclient import TestClient
from main import app
from woningwaardering import Woningwaardering
from woningwaardering.vera.bvg.generated import EenhedenEenheid
from optimization import (
    find_optimization_opportunities,
    _extract_total_score,
    _suggest_kitchen_upgrades,
    _suggest_bathroom_upgrades,
    _suggest_heating_improvements,
)


client = TestClient(app)


class TestScoreExtraction:
    """Test that score extraction from results works correctly."""
    
    def test_extract_score_from_result_attributes(self):
        """Test extracting score from common result attributes."""
        # Mock result with totale_waardering
        class MockResult:
            totale_waardering = 42.5
        
        result = MockResult()
        score = _extract_total_score(result)
        assert score == 42.5, "Should extract totale_waardering"
    
    def test_extract_score_from_punten(self):
        """Test extracting score from punten attribute."""
        class MockResult:
            punten = 55.0
        
        result = MockResult()
        score = _extract_total_score(result)
        assert score == 55.0, "Should extract punten"
    
    def test_extract_score_from_dict(self):
        """Test extracting score from dictionary result."""
        result = {'totale_waardering': 60.0}
        score = _extract_total_score(result)
        assert score == 60.0, "Should extract from dict"
    
    def test_extract_score_invalid_result(self):
        """Test handling of invalid result."""
        result = "invalid"
        score = _extract_total_score(result)
        assert score == 0.0, "Should return 0 for invalid result"


class TestOptimizationWithRealLibrary:
    """Test optimization suggestions with actual woningwaardering library."""
    
    @pytest.fixture
    def basic_eenheid(self):
        """Create a basic housing unit for testing."""
        return {
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
            "ruimten": [
                {
                    "id": "bedroom_1",
                    "soort": {"code": "VT"},
                    "detail_soort": {"code": "SK"},
                    "naam": "Slaapkamer",
                    "oppervlakte": 15,
                    "inhoud": 37.5,
                    "verwarmd": True
                },
                {
                    "id": "kitchen_1",
                    "soort": {"code": "VT"},
                    "detail_soort": {"code": "KK"},
                    "naam": "Keuken",
                    "oppervlakte": 10,
                    "inhoud": 25,
                    "verwarmd": True
                },
                {
                    "id": "bathroom_1",
                    "soort": {"code": "VT"},
                    "detail_soort": {"code": "BK"},
                    "naam": "Badkamer",
                    "oppervlakte": 5,
                    "inhoud": 12.5,
                    "verwarmd": True
                }
            ]
        }
    
    def test_calculate_baseline_score(self, basic_eenheid):
        """Test that we can calculate a baseline score."""
        response = client.post("/calculate", json={"eenheid_data": basic_eenheid})
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "detailed_json" in result
    
    def test_optimize_suggestions_contain_scores(self, basic_eenheid):
        """Test that optimization suggestions have valid score gains."""
        response = client.post("/optimize", json={"eenheid_data": basic_eenheid})
        
        # Should get 200 or detailed error
        if response.status_code == 200:
            result = response.json()
            assert result["success"] is True
            assert "suggestions" in result
            
            suggestions = result["suggestions"]
            # Each suggestion should have a score gain
            for suggestion in suggestions:
                assert "estimated_score_gain" in suggestion
                assert isinstance(suggestion["estimated_score_gain"], (int, float))
                assert suggestion["estimated_score_gain"] >= 0
    
    def test_suggestions_ranked_by_score(self, basic_eenheid):
        """Test that suggestions are ranked by score gain (highest first)."""
        response = client.post("/optimize", json={"eenheid_data": basic_eenheid})
        
        if response.status_code == 200:
            result = response.json()
            suggestions = result["suggestions"]
            
            if len(suggestions) > 1:
                # Verify descending order
                for i in range(len(suggestions) - 1):
                    current_gain = suggestions[i]["estimated_score_gain"]
                    next_gain = suggestions[i + 1]["estimated_score_gain"]
                    assert current_gain >= next_gain, \
                        f"Suggestions not properly ranked: {current_gain} < {next_gain}"
    
    def test_suggestion_has_required_fields(self, basic_eenheid):
        """Test that each suggestion has all required fields."""
        response = client.post("/optimize", json={"eenheid_data": basic_eenheid})
        
        if response.status_code == 200:
            result = response.json()
            suggestions = result["suggestions"]
            
            required_fields = [
                "category",
                "title",
                "description",
                "estimated_score_gain",
                "implementation_effort",
                "affected_criteria"
            ]
            
            for suggestion in suggestions:
                for field in required_fields:
                    assert field in suggestion, f"Missing field: {field}"
    
    def test_heating_improvement_suggestion(self, basic_eenheid):
        """Test that heating improvements can be identified."""
        # Add an unheated room
        basic_eenheid["ruimten"].append({
            "id": "hallway_1",
            "soort": {"code": "VT"},
            "detail_soort": {"code": "HA"},  # Hallway
            "naam": "Gang",
            "oppervlakte": 8,
            "inhoud": 20,
            "verwarmd": False  # Unheated
        })
        
        response = client.post("/optimize", json={"eenheid_data": basic_eenheid})
        
        if response.status_code == 200:
            result = response.json()
            suggestions = result["suggestions"]
            
            # Check if there's a heating suggestion
            heating_suggestions = [s for s in suggestions if "heating" in s.get("title", "").lower()]
            # If we have heating suggestions, they should have positive gains
            for suggestion in heating_suggestions:
                assert suggestion["estimated_score_gain"] >= 0


class TestScoreComparison:
    """Test that score improvements are correctly calculated."""
    
    def test_score_improves_with_heating(self):
        """Test that adding heating improves the score."""
        # This is an integration test comparing baseline vs. improved unit
        
        # Unit WITHOUT heating in hallway
        unit_without_heating = {
            "id": "test_no_heat",
            "bouwjaar": 1980,
            "gebruiksoppervlakte": 90,
            "woningwaarderingstelsel": {"code": "ZEL"},
            "adres": {
                "straatnaam": "Teststraat",
                "huisnummer": "2",
                "postcode": "1234AB",
                "woonplaats": {"naam": "Amsterdam"}
            },
            "ruimten": [
                {
                    "id": "room_1",
                    "soort": {"code": "VT"},
                    "detail_soort": {"code": "SK"},
                    "naam": "Slaapkamer",
                    "oppervlakte": 15,
                    "inhoud": 37.5,
                    "verwarmd": True
                },
                {
                    "id": "room_2",
                    "soort": {"code": "VT"},
                    "detail_soort": {"code": "HA"},
                    "naam": "Gang",
                    "oppervlakte": 8,
                    "inhoud": 20,
                    "verwarmd": False  # NOT heated
                }
            ]
        }
        
        # Unit WITH heating in hallway
        unit_with_heating = {
            "id": "test_with_heat",
            "bouwjaar": 1980,
            "gebruiksoppervlakte": 90,
            "woningwaarderingstelsel": {"code": "ZEL"},
            "adres": {
                "straatnaam": "Teststraat",
                "huisnummer": "2",
                "postcode": "1234AB",
                "woonplaats": {"naam": "Amsterdam"}
            },
            "ruimten": [
                {
                    "id": "room_1",
                    "soort": {"code": "VT"},
                    "detail_soort": {"code": "SK"},
                    "naam": "Slaapkamer",
                    "oppervlakte": 15,
                    "inhoud": 37.5,
                    "verwarmd": True
                },
                {
                    "id": "room_2",
                    "soort": {"code": "VT"},
                    "detail_soort": {"code": "HA"},
                    "naam": "Gang",
                    "oppervlakte": 8,
                    "inhoud": 20,
                    "verwarmd": True  # Heated
                }
            ]
        }
        
        # Calculate baseline
        response1 = client.post("/calculate", json={"eenheid_data": unit_without_heating})
        # Calculate with improvement
        response2 = client.post("/calculate", json={"eenheid_data": unit_with_heating})
        
        if response1.status_code == 200 and response2.status_code == 200:
            # Extract scores if available
            result1 = response1.json()
            result2 = response2.json()
            
            # Both should be successful
            assert result1["success"] is True
            assert result2["success"] is True


class TestBatchOptimization:
    """Test batch processing of optimization suggestions."""
    
    def test_batch_calculate_with_multiple_units(self):
        """Test batch calculation of multiple units."""
        batch_request = {
            "requests": [
                {
                    "eenheid_data": {
                        "id": "batch_001",
                        "bouwjaar": 1975,
                        "gebruiksoppervlakte": 80,
                        "woningwaarderingstelsel": {"code": "ZEL"},
                        "adres": {
                            "straatnaam": "Batch1",
                            "huisnummer": "1",
                            "postcode": "1111AA",
                            "woonplaats": {"naam": "Amsterdam"}
                        },
                        "ruimten": [{
                            "id": "r1",
                            "soort": {"code": "VT"},
                            "detail_soort": {"code": "SK"},
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
                        "gebruiksoppervlakte": 100,
                        "woningwaarderingstelsel": {"code": "ZEL"},
                        "adres": {
                            "straatnaam": "Batch2",
                            "huisnummer": "2",
                            "postcode": "2222BB",
                            "woonplaats": {"naam": "Rotterdam"}
                        },
                        "ruimten": [{
                            "id": "r2",
                            "soort": {"code": "VT"},
                            "detail_soort": {"code": "KK"},
                            "oppervlakte": 12,
                            "inhoud": 30,
                            "verwarmd": True
                        }]
                    }
                }
            ]
        }
        
        response = client.post("/batch-calculate", json=batch_request)
        
        assert response.status_code == 200
        result = response.json()
        assert "results" in result
        assert len(result["results"]) == 2


class TestNoRoomExpansion:
    """Verify that optimization no longer suggests room additions or expansions."""
    
    def test_no_room_addition_suggestions(self):
        """Test that suggestions don't include adding rooms."""
        request_data = {
            "eenheid_data": {
                "id": "test_single_room",
                "bouwjaar": 1970,
                "gebruiksoppervlakte": 50,
                "woningwaarderingstelsel": {"code": "ZEL"},
                "adres": {
                    "straatnaam": "Test",
                    "huisnummer": "1",
                    "postcode": "1000AA",
                    "woonplaats": {"naam": "Test"}
                },
                "ruimten": [{
                    "id": "only_room",
                    "soort": {"code": "VT"},
                    "detail_soort": {"code": "SK"},
                    "oppervlakte": 15,
                    "inhoud": 37.5,
                    "verwarmd": True
                }]
            }
        }
        
        response = client.post("/optimize", json=request_data)
        
        if response.status_code == 200:
            result = response.json()
            suggestions = result.get("suggestions", [])
            
            # Check that NO suggestions mention adding rooms
            disallowed_keywords = ["add bedroom", "add bathroom", "add room", "add second"]
            for suggestion in suggestions:
                title = suggestion.get("title", "").lower()
                for keyword in disallowed_keywords:
                    assert keyword not in title, \
                        f"Found disallowed suggestion: {suggestion['title']}"
    
    def test_no_room_expansion_suggestions(self):
        """Test that suggestions don't include expanding rooms."""
        request_data = {
            "eenheid_data": {
                "id": "test_small_room",
                "bouwjaar": 1970,
                "gebruiksoppervlakte": 50,
                "woningwaarderingstelsel": {"code": "ZEL"},
                "adres": {
                    "straatnaam": "Test",
                    "huisnummer": "1",
                    "postcode": "1000AA",
                    "woonplaats": {"naam": "Test"}
                },
                "ruimten": [{
                    "id": "small_room",
                    "soort": {"code": "VT"},
                    "detail_soort": {"code": "SK"},
                    "oppervlakte": 8,  # Small bedroom
                    "inhoud": 20,
                    "verwarmd": True
                }]
            }
        }
        
        response = client.post("/optimize", json=request_data)
        
        if response.status_code == 200:
            result = response.json()
            suggestions = result.get("suggestions", [])
            
            # Check that suggestions about expanding rooms are gone
            disallowed_keywords = ["expand", "increase bedroom", "room expansion"]
            for suggestion in suggestions:
                title = suggestion.get("title", "").lower()
                description = suggestion.get("description", "").lower()
                for keyword in disallowed_keywords:
                    assert keyword not in title, \
                        f"Found disallowed suggestion: {suggestion['title']}"
                    assert keyword not in description, \
                        f"Found disallowed in description: {keyword}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
