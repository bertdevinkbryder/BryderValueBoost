"""
Optimization and space exploration utilities for finding ways to improve woning waarde.
Focuses on space-efficient improvements within the existing building footprint.
"""

import logging
from typing import List, Optional, Dict, Any
from copy import deepcopy
from datetime import date

from woningwaardering import Woningwaardering
from woningwaardering.vera.bvg.generated import (
    EenhedenEenheid,
    EenhedenRuimte,
    BouwkundigElementenBouwkundigElement,
)
from woningwaardering.vera.referentiedata import (
    Ruimtesoort,
    Ruimtedetailsoort,
    Bouwkundigelementsoort,
)

from models import OptimizationSuggestion, OptimizationCategory

logger = logging.getLogger(__name__)


def find_optimization_opportunities(
    eenheid: EenhedenEenheid,
    wws: Woningwaardering,
    baseline_result: Any,
    peildatum: date,
    max_suggestions: int = 10
) -> List[OptimizationSuggestion]:
    """
    Analyze a housing unit and find optimization opportunities to improve woning waarde.
    
    FOCUS: Space-efficient improvements ONLY - no adding floor space or new rooms.
    This includes:
    1. Upgrading existing fixtures (kitchen counters, bathroom fixtures)
    2. Adding heating to unheated rooms
    3. Improving ventilation and air quality
    4. Better room layout optimization
    5. Upgrading built-in elements (windows, doors, insulation)
    
    Args:
        eenheid: Housing unit to analyze
        wws: Woningwaardering calculator instance
        baseline_result: Current calculation result
        peildatum: Valuation date
        max_suggestions: Maximum number of suggestions to return
    
    Returns:
        List of optimization suggestions sorted by score improvement potential
    """
    
    suggestions: List[OptimizationSuggestion] = []
    
    # 1. Upgrade kitchen facilities (within existing kitchen space)
    try:
        suggestions.extend(_suggest_kitchen_upgrades(eenheid, wws, peildatum))
    except Exception as e:
        logger.debug(f"Kitchen upgrades failed: {e}")
    
    # 2. Upgrade bathroom fixtures (within existing bathroom)
    try:
        suggestions.extend(_suggest_bathroom_upgrades(eenheid, wws, peildatum))
    except Exception as e:
        logger.debug(f"Bathroom upgrades failed: {e}")
    
    # 3. Add heating to unheated rooms
    try:
        suggestions.extend(_suggest_heating_improvements(eenheid, wws, peildatum))
    except Exception as e:
        logger.debug(f"Heating improvements failed: {e}")
    
    # 4. Improve ventilation and air quality
    try:
        suggestions.extend(_suggest_ventilation_improvements(eenheid, wws, peildatum))
    except Exception as e:
        logger.debug(f"Ventilation improvements failed: {e}")
    
    # 5. Upgrade existing elements (windows, doors, insulation indicators)
    try:
        suggestions.extend(_suggest_element_quality_upgrades(eenheid, wws, peildatum))
    except Exception as e:
        logger.debug(f"Element quality upgrades failed: {e}")
    
    # 6. Improve energy efficiency (better insulation, heating systems)
    try:
        suggestions.extend(_suggest_energy_efficiency_improvements(eenheid, wws, peildatum))
    except Exception as e:
        logger.debug(f"Energy efficiency improvements failed: {e}")
    
    # Sort by estimated score gain (highest first)
    suggestions.sort(key=lambda x: x.estimated_score_gain, reverse=True)
    
    # Return top suggestions
    return suggestions[:max_suggestions]


def _suggest_kitchen_upgrades(
    eenheid: EenhedenEenheid,
    wws: Woningwaardering,
    peildatum: date
) -> List[OptimizationSuggestion]:
    """
    Suggest upgrades to existing kitchen within same space.
    No room expansion - just better fixtures and storage.
    """
    suggestions: List[OptimizationSuggestion] = []
    
    baseline_result = wws.waardeer(eenheid)
    baseline_score = _extract_total_score(baseline_result)
    
    current_rooms = eenheid.ruimten or []
    
    try:
        from woningwaardering.vera.referentiedata import Bouwkundigelementdetailsoort
    except (ImportError, AttributeError):
        return suggestions
    
    # Find kitchen
    for room in current_rooms:
        if room.detail_soort == Ruimtedetailsoort.keuken:
            current_elements = room.bouwkundige_elementen or []
            element_types = {getattr(elem, 'detail_soort', None) for elem in current_elements}
            
            # Upgrade 1: Improve counter size
            aanrecht = None
            for elem in current_elements:
                if getattr(elem, 'detail_soort', None) == Bouwkundigelementdetailsoort.aanrecht:
                    aanrecht = elem
                    break
            
            if aanrecht and aanrecht.lengte:
                current_length = aanrecht.lengte
                # Test upgrading counter (e.g., 150cm -> 195cm or better distribution)
                test_eenheid = deepcopy(eenheid)
                for test_room in test_eenheid.ruimten:
                    if test_room.id == room.id and test_room.bouwkundige_elementen:
                        for test_elem in test_room.bouwkundige_elementen:
                            if getattr(test_elem, 'id', None) == aanrecht.id:
                                # Upgrade to better counter
                                new_length = min(current_length * 1.25, 250)  # Better size
                                test_elem.lengte = new_length
                
                try:
                    test_result = wws.waardeer(test_eenheid)
                    test_score = _extract_total_score(test_result)
                    score_gain = test_score - baseline_score
                    
                    if score_gain > 0:
                        suggestions.append(OptimizationSuggestion(
                            category=OptimizationCategory.SPACE_OPTIMIZATION,
                            title=f"Upgrade Kitchen Counter (from {current_length:.0f}cm to {new_length:.0f}cm)",
                            description="Better counter layout and size improves kitchen functionality without expanding space",
                            estimated_score_gain=float(score_gain),
                            implementation_effort="low",
                            estimated_cost_indication="€500 - €2,000",
                            affected_criteria=["kitchen_functionality", "workspace"]
                        ))
                except Exception as e:
                    logger.debug(f"Error testing counter upgrade: {e}")
            
            # Upgrade 2: Add built-in storage/cupboards
            has_cabinet = hasattr(Bouwkundigelementdetailsoort, 'kast') and Bouwkundigelementdetailsoort.kast in element_types
            if not has_cabinet:
                test_eenheid = deepcopy(eenheid)
                for test_room in test_eenheid.ruimten:
                    if test_room.id == room.id:
                        if test_room.bouwkundige_elementen is None:
                            test_room.bouwkundige_elementen = []
                        
                        cupboard = BouwkundigElementenBouwkundigElement(
                            id="kast_test",
                            naam="Kastopstelling",
                            soort={"code": "OVE"},
                            detail_soort={"code": "KAST"},
                            lengte=2000
                        )
                        test_room.bouwkundige_elementen.append(cupboard)
                
                try:
                    test_result = wws.waardeer(test_eenheid)
                    test_score = _extract_total_score(test_result)
                    score_gain = test_score - baseline_score
                    
                    if score_gain > 0:
                        suggestions.append(OptimizationSuggestion(
                            category=OptimizationCategory.SPACE_OPTIMIZATION,
                            title="Add Built-in Kitchen Storage/Cupboards",
                            description="Built-in storage optimizes space and improves kitchen functionality",
                            estimated_score_gain=float(score_gain),
                            implementation_effort="low",
                            estimated_cost_indication="€1,500 - €4,000",
                            affected_criteria=["storage_space", "kitchen_quality"]
                        ))
                except Exception as e:
                    logger.debug(f"Error testing cupboard upgrade: {e}")
            
            # Upgrade 3: Add sink if missing
            has_sink = hasattr(Bouwkundigelementdetailsoort, 'spoelbak') and Bouwkundigelementdetailsoort.spoelbak in element_types
            if not has_sink:
                test_eenheid = deepcopy(eenheid)
                for test_room in test_eenheid.ruimten:
                    if test_room.id == room.id:
                        if test_room.bouwkundige_elementen is None:
                            test_room.bouwkundige_elementen = []
                        
                        sink = BouwkundigElementenBouwkundigElement(
                            id="spoelbak_test",
                            naam="Spoelbak",
                            soort={"code": "VOO"},
                            detail_soort={"code": "SPOELBAK"},
                            lengte=600
                        )
                        test_room.bouwkundige_elementen.append(sink)
                
                try:
                    test_result = wws.waardeer(test_eenheid)
                    test_score = _extract_total_score(test_result)
                    score_gain = test_score - baseline_score
                    
                    if score_gain > 0:
                        suggestions.append(OptimizationSuggestion(
                            category=OptimizationCategory.FACILITIES,
                            title="Add Kitchen Sink/Washbasin",
                            description="Adding a kitchen sink is essential for functionality",
                            estimated_score_gain=float(score_gain),
                            implementation_effort="medium",
                            estimated_cost_indication="€1,000 - €2,500",
                            affected_criteria=["kitchen_functionality", "sanitary_facilities"]
                        ))
                except Exception as e:
                    logger.debug(f"Error testing sink: {e}")
    
    return suggestions


def _suggest_bathroom_upgrades(
    eenheid: EenhedenEenheid,
    wws: Woningwaardering,
    peildatum: date
) -> List[OptimizationSuggestion]:
    """
    Suggest upgrades to existing bathrooms within same space.
    Add missing fixtures (shower, toilet) without expanding.
    """
    suggestions: List[OptimizationSuggestion] = []
    
    baseline_result = wws.waardeer(eenheid)
    baseline_score = _extract_total_score(baseline_result)
    
    current_rooms = eenheid.ruimten or []
    
    try:
        from woningwaardering.vera.referentiedata import Bouwkundigelementdetailsoort
    except (ImportError, AttributeError):
        return suggestions
    
    # Find bathrooms
    bathrooms = [room for room in current_rooms 
                 if room.detail_soort == Ruimtedetailsoort.badkamer]
    
    for bathroom in bathrooms:
        elements = bathroom.bouwkundige_elementen or []
        element_types = {getattr(e, 'detail_soort', None) for e in elements}
        
        # Upgrade 1: Add shower if only bathtub exists
        # Safely check for attributes that might not exist in this library version
        try:
            has_bath = hasattr(Bouwkundigelementdetailsoort, 'bad') and Bouwkundigelementdetailsoort.bad in element_types
            has_shower = hasattr(Bouwkundigelementdetailsoort, 'douchebak') and Bouwkundigelementdetailsoort.douchebak in element_types
        except (AttributeError, TypeError):
            has_bath = False
            has_shower = False
        
        if has_bath and not has_shower:
            test_eenheid = deepcopy(eenheid)
            for test_room in test_eenheid.ruimten:
                if test_room.id == bathroom.id:
                    if test_room.bouwkundige_elementen is None:
                        test_room.bouwkundige_elementen = []
                    
                    shower = BouwkundigElementenBouwkundigElement(
                        id="shower_test",
                        naam="Douchebak",
                        soort={"code": "VOO"},
                        detail_soort={"code": "DOUCHEBAK"},
                        lengte=800
                    )
                    test_room.bouwkundige_elementen.append(shower)
            
            try:
                test_result = wws.waardeer(test_eenheid)
                test_score = _extract_total_score(test_result)
                score_gain = test_score - baseline_score
                
                if score_gain > 0:
                    suggestions.append(OptimizationSuggestion(
                        category=OptimizationCategory.FACILITIES,
                        title="Add Shower to Bathroom",
                        description="Adding a shower alongside existing bathtub improves bathroom functionality without expanding space",
                        estimated_score_gain=float(score_gain),
                        implementation_effort="medium",
                        estimated_cost_indication="€2,000 - €5,000",
                        affected_criteria=["bathroom_quality", "sanitary_fixtures"]
                    ))
            except Exception as e:
                logger.debug(f"Error testing shower upgrade: {e}")
        
        # Upgrade 2: Add toilet if missing
        has_toilet = hasattr(Bouwkundigelementdetailsoort, 'toilet') and Bouwkundigelementdetailsoort.toilet in element_types
        
        if not has_toilet:
            test_eenheid = deepcopy(eenheid)
            for test_room in test_eenheid.ruimten:
                if test_room.id == bathroom.id:
                    if test_room.bouwkundige_elementen is None:
                        test_room.bouwkundige_elementen = []
                    
                    toilet = BouwkundigElementenBouwkundigElement(
                        id="toilet_test",
                        naam="Toilet",
                        soort={"code": "VOO"},
                        detail_soort={"code": "TOILET"},
                        lengte=600
                    )
                    test_room.bouwkundige_elementen.append(toilet)
            
            try:
                test_result = wws.waardeer(test_eenheid)
                test_score = _extract_total_score(test_result)
                score_gain = test_score - baseline_score
                
                if score_gain > 0:
                    suggestions.append(OptimizationSuggestion(
                        category=OptimizationCategory.FACILITIES,
                        title="Add Toilet to Bathroom",
                        description="Having toilet in bathroom improves convenience and score",
                        estimated_score_gain=float(score_gain),
                        implementation_effort="high",
                        estimated_cost_indication="€1,500 - €4,000",
                        affected_criteria=["bathroom_convenience", "layout_efficiency"]
                    ))
            except Exception as e:
                logger.debug(f"Error testing toilet addition: {e}")
    
    return suggestions


def _suggest_heating_improvements(
    eenheid: EenhedenEenheid,
    wws: Woningwaardering,
    peildatum: date
) -> List[OptimizationSuggestion]:
    """
    Suggest adding heating to currently unheated rooms.
    """
    suggestions: List[OptimizationSuggestion] = []
    
    baseline_result = wws.waardeer(eenheid)
    baseline_score = _extract_total_score(baseline_result)
    
    current_rooms = eenheid.ruimten or []
    
    # Find unheated rooms
    for room in current_rooms:
        if not room.verwarmd:
            test_eenheid = deepcopy(eenheid)
            for test_room in test_eenheid.ruimten:
                if test_room.id == room.id:
                    test_room.verwarmd = True
            
            try:
                test_result = wws.waardeer(test_eenheid)
                test_score = _extract_total_score(test_result)
                score_gain = test_score - baseline_score
                
                if score_gain > 0:
                    suggestions.append(OptimizationSuggestion(
                        category=OptimizationCategory.HEATING,
                        title=f"Add Heating to {room.naam or 'Unheated Room'}",
                        description="Installing heating in unheated rooms (hallways, storage, entryways) increases comfort and reduces energy loss",
                        estimated_score_gain=float(score_gain),
                        implementation_effort="medium",
                        estimated_cost_indication="€800 - €2,500",
                        affected_criteria=["heating", "comfort", "energy_efficiency"]
                    ))
            except Exception as e:
                logger.debug(f"Error testing heating: {e}")
    
    return suggestions


def _suggest_ventilation_improvements(
    eenheid: EenhedenEenheid,
    wws: Woningwaardering,
    peildatum: date
) -> List[OptimizationSuggestion]:
    """
    Suggest adding ventilation to improve air quality.
    """
    suggestions: List[OptimizationSuggestion] = []
    
    baseline_result = wws.waardeer(eenheid)
    baseline_score = _extract_total_score(baseline_result)
    
    current_rooms = eenheid.ruimten or []
    
    try:
        from woningwaardering.vera.referentiedata import Bouwkundigelementdetailsoort
    except (ImportError, AttributeError):
        return suggestions
    
    # Test adding ventilation to small rooms or kitchens/bathrooms
    for room in current_rooms:
        # Kitchens and bathrooms benefit from mechanical ventilation
        needs_ventilation = room.detail_soort in [
            Ruimtedetailsoort.keuken,
            Ruimtedetailsoort.badkamer
        ]
        
        # Or very small rooms
        if room.oppervlakte and room.oppervlakte < 8:
            needs_ventilation = True
        
        if needs_ventilation:
            elements = room.bouwkundige_elementen or []
            # Safely check for ventilation attribute
            try:
                ventilatie_attr = Bouwkundigelementdetailsoort.ventilatie if hasattr(Bouwkundigelementdetailsoort, 'ventilatie') else None
                has_ventilation = ventilatie_attr and any(
                    getattr(e, 'detail_soort', None) == ventilatie_attr 
                    for e in elements
                )
            except (AttributeError, TypeError):
                has_ventilation = False
            
            if not has_ventilation and hasattr(Bouwkundigelementdetailsoort, 'ventilatie'):
                test_eenheid = deepcopy(eenheid)
                for test_room in test_eenheid.ruimten:
                    if test_room.id == room.id:
                        if test_room.bouwkundige_elementen is None:
                            test_room.bouwkundige_elementen = []
                        
                        ventilation = BouwkundigElementenBouwkundigElement(
                            id="ventilation_test",
                            naam="Ventilatie",
                            soort={"code": "OVE"},
                            detail_soort={"code": "VENTILATIE"},
                            lengte=100
                        )
                        test_room.bouwkundige_elementen.append(ventilation)
                
                try:
                    test_result = wws.waardeer(test_eenheid)
                    test_score = _extract_total_score(test_result)
                    score_gain = test_score - baseline_score
                    
                    if score_gain > 0.01:
                        room_type = room.naam or "Room"
                        suggestions.append(OptimizationSuggestion(
                            category=OptimizationCategory.FACILITIES,
                            title=f"Add Ventilation to {room_type}",
                            description="Mechanical ventilation prevents moisture, mold, and improves air quality",
                            estimated_score_gain=float(score_gain),
                            implementation_effort="low",
                            estimated_cost_indication="€300 - €1,500",
                            affected_criteria=["ventilation", "air_quality", "moisture_control"]
                        ))
                except Exception as e:
                    logger.debug(f"Error testing ventilation: {e}")
    
    return suggestions


def _suggest_element_quality_upgrades(
    eenheid: EenhedenEenheid,
    wws: Woningwaardering,
    peildatum: date
) -> List[OptimizationSuggestion]:
    """
    Suggest upgrading quality of existing elements (windows, doors, insulation).
    """
    suggestions: List[OptimizationSuggestion] = []
    
    baseline_result = wws.waardeer(eenheid)
    baseline_score = _extract_total_score(baseline_result)
    
    current_rooms = eenheid.ruimten or []
    
    try:
        from woningwaardering.vera.referentiedata import Bouwkundigelementdetailsoort
    except (ImportError, AttributeError):
        return suggestions
    
    # Test upgrading to double-glazing (windows)
    # This is indicated by adding/upgrading window elements
    # Safeguard for missing raam attribute
    try:
        _ = Bouwkundigelementdetailsoort.raam
        raam_available = True
    except AttributeError:
        raam_available = False
    
    if not raam_available:
        return suggestions  # Skip if raam attribute doesn't exist
    
    for room in current_rooms:
        elements = room.bouwkundige_elementen or []
        has_windows = any(
            getattr(e, 'detail_soort', None) == Bouwkundigelementdetailsoort.raam 
            for e in elements
        )
        
        # If room has no window element, test adding better ones
        if not has_windows and hasattr(Bouwkundigelementdetailsoort, 'raam'):
            test_eenheid = deepcopy(eenheid)
            for test_room in test_eenheid.ruimten:
                if test_room.id == room.id:
                    if test_room.bouwkundige_elementen is None:
                        test_room.bouwkundige_elementen = []
                    
                    window = BouwkundigElementenBouwkundigElement(
                        id="window_test",
                        naam="Raam (dubbel glas)",
                        soort={"code": "OVE"},
                        detail_soort={"code": "RAAM"},
                        lengte=1200
                    )
                    test_room.bouwkundige_elementen.append(window)
            
            try:
                test_result = wws.waardeer(test_eenheid)
                test_score = _extract_total_score(test_result)
                score_gain = test_score - baseline_score
                
                if score_gain > 0:
                    suggestions.append(OptimizationSuggestion(
                        category=OptimizationCategory.INSULATION,
                        title=f"Upgrade Windows in {room.naam or 'Room'} to Double-Glazed",
                        description="Double-glazed windows improve insulation, reduce noise, and enhance comfort",
                        estimated_score_gain=float(score_gain),
                        implementation_effort="high",
                        estimated_cost_indication="€2,000 - €8,000",
                        affected_criteria=["insulation", "thermal_comfort", "noise_reduction"]
                    ))
            except Exception as e:
                logger.debug(f"Error testing window upgrade: {e}")
    
    return suggestions


def _suggest_energy_efficiency_improvements(
    eenheid: EenhedenEenheid,
    wws: Woningwaardering,
    peildatum: date
) -> List[OptimizationSuggestion]:
    """
    Suggest energy efficiency improvements (better insulation, systems, energy labels).
    """
    suggestions: List[OptimizationSuggestion] = []
    
    baseline_result = wws.waardeer(eenheid)
    baseline_score = _extract_total_score(baseline_result)
    
    # Test: Improve energy performance label
    energieprestaties = eenheid.energieprestaties or []
    
    if energieprestaties:
        current_label = energieprestaties[-1].label if energieprestaties else None
        
        if current_label and current_label != "A":
            test_eenheid = deepcopy(eenheid)
            
            # Simulate improving to better label
            from woningwaardering.vera.referentiedata import Energielabel
            
            label_hierarchy = [Energielabel.g, Energielabel.f, Energielabel.e, 
                              Energielabel.d, Energielabel.c, Energielabel.b, Energielabel.a]
            
            try:
                current_idx = label_hierarchy.index(current_label)
                if current_idx > 0:
                    improved_label = label_hierarchy[current_idx - 1]
                    if test_eenheid.energieprestaties:
                        test_eenheid.energieprestaties[-1].label = improved_label
                    
                    test_result = wws.waardeer(test_eenheid)
                    test_score = _extract_total_score(test_result)
                    score_gain = test_score - baseline_score
                    
                    if score_gain > 0:
                        suggestions.append(OptimizationSuggestion(
                            category=OptimizationCategory.INSULATION,
                            title=f"Improve Energy Label from {current_label.value} to {improved_label.value}",
                            description="Better insulation, efficient heating systems, and upgrades improve energy performance",
                            estimated_score_gain=float(score_gain),
                            implementation_effort="high",
                            estimated_cost_indication="€8,000 - €30,000",
                            affected_criteria=["energy_performance", "sustainability", "utility_costs"]
                        ))
            except (ValueError, AttributeError):
                pass
    
    return suggestions


def _extract_total_score(result: Any) -> float:
    """
    Extract total score from the woning waarde result object.
    
    Tries multiple common attribute names and formats.
    """
    try:
        # Try common attribute names
        if hasattr(result, 'totale_waardering'):
            return float(result.totale_waardering)
        if hasattr(result, 'waardering'):
            return float(result.waardering)
        if hasattr(result, 'punten'):
            return float(result.punten)
        if hasattr(result, 'score'):
            return float(result.score)
        
        # Try as dictionary
        if isinstance(result, dict):
            for key in ['totale_waardering', 'waardering', 'punten', 'score', 'total']:
                if key in result:
                    return float(result[key])
        
        logger.warning("Could not extract total score from result")
        return 0.0
    except (AttributeError, ValueError, TypeError) as e:
        logger.error(f"Error extracting score: {e}")
        return 0.0
