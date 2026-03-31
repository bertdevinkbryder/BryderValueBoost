"""
Data models for the Woningwaardering API.
"""

from pydantic import BaseModel, Field
from datetime import date
from typing import List, Optional, Any, Dict
from enum import Enum


class OptimizationCategory(str, Enum):
    """Categories of optimization opportunities."""
    ROOM_IMPROVEMENT = "room_improvement"
    SPACE_OPTIMIZATION = "space_optimization"
    INSULATION = "insulation"
    HEATING = "heating"
    FACILITIES = "facilities"
    STRUCTURAL = "structural"
    OTHER = "other"


class OptimizationSuggestion(BaseModel):
    """A suggestion for improving the woning waarde score."""
    
    category: OptimizationCategory = Field(..., description="Category of the improvement")
    title: str = Field(..., description="Short title of the suggestion")
    description: str = Field(..., description="Detailed description of the improvement")
    estimated_score_gain: float = Field(..., description="Estimated increase in woning waarde score")
    implementation_effort: str = Field(..., description="Level of effort (low, medium, high)")
    estimated_cost_indication: Optional[str] = Field(None, description="Cost indication if known")
    affected_criteria: List[str] = Field(default_factory=list, description="Which scoring criteria are affected")
    example_modification: Optional[Dict[str, Any]] = Field(None, description="Example JSON modification to apply")


class WoningwaarderingRequest(BaseModel):
    """Request model for woning waarde calculation."""
    
    eenheid_data: Dict[str, Any] = Field(
        ..., 
        description="Housing unit data in VERA standard format (EenhedenEenheid)"
    )
    peildatum: Optional[date] = Field(
        None, 
        description="Valuation date (defaults to today if not provided)"
    )


class WoningwaarderingResponse(BaseModel):
    """Response model for woning waarde calculation."""
    
    success: bool = Field(..., description="Whether the calculation was successful")
    message: str = Field(..., description="Response message")
    eenheid_id: str = Field(..., description="ID of the housing unit")
    peildatum: date = Field(..., description="The valuation date used")
    detailed_json: str = Field(..., description="Detailed JSON output with all scoring details")
    table_output: str = Field(..., description="Table format output for easy reading")
    raw_result: Optional[Any] = Field(None, description="Raw result object for further processing")


class HealthCheckResponse(BaseModel):
    """Response model for health check."""
    
    status: str = Field(..., description="Status of the API")


# For batch operations
from typing import List

class BatchCalculateRequest(BaseModel):
    """Request for batch calculations."""
    requests: List[WoningwaarderingRequest]


class OptimizationSuggestion(BaseModel):
    """A suggestion for improving woning waarde."""
    
    category: str
    title: str
    description: str
    estimated_score_gain: float
    implementation_effort: str
    estimated_cost_indication: Optional[str] = None
    affected_criteria: List[str] = []
    example_modification: Optional[Dict[str, Any]] = None

    class Config:
        use_enum_values = True

    def dict(self, **kwargs):
        """Convert to dictionary."""
        d = super().dict(**kwargs)
        return d
