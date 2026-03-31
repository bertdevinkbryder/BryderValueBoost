"""
RESTful API for Woningwaardering calculations and optimization.
"""

from fastapi import FastAPI, HTTPException
from datetime import date
import logging
from typing import Optional, List
import uvicorn

from woningwaardering import Woningwaardering
from woningwaardering.stelsels.utils import naar_tabel
from woningwaardering.vera.bvg.generated import EenhedenEenheid

from models import WoningwaarderingRequest, WoningwaarderingResponse, OptimizationSuggestion, HealthCheckResponse
from optimization import find_optimization_opportunities

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Woningwaardering API",
    description="API for calculating and optimizing woning waarde scores",
    version="1.0.0"
)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/calculate", response_model=WoningwaarderingResponse)
async def calculate_woning_waarde(request: WoningwaarderingRequest):
    """
    Calculate the woning waarde based on a JSON input representing an EenhedenEenheid.
    
    The input JSON should follow the VERA standard format for EenhedenEenheid.
    Returns detailed scoring information and table format output.
    """
    try:
        # Parse the JSON input to EenhedenEenheid
        eenheid = EenhedenEenheid.model_validate(request.eenheid_data)
        
        # Use provided peildatum or default to today
        peildatum = request.peildatum or date.today()
        
        # Initialize Woningwaardering calculator with peildatum
        wws = Woningwaardering(peildatum=peildatum)
        
        # Calculate woning waarde - waardeer method returns the result
        woningwaardering_resultaat = wws.waardeer(eenheid)
        
        # Get JSON output
        try:
            json_output = woningwaardering_resultaat.model_dump_json(
                by_alias=True, indent=2, exclude_none=True
            )
        except:
            json_output = str(woningwaardering_resultaat)
        
        # Generate table output
        try:
            tabel = naar_tabel(woningwaardering_resultaat)
            table_output = str(tabel)
        except:
            table_output = "Table format not available"
        
        eenheid_id = getattr(eenheid, 'id', 'unknown')
        logger.info(f"Successfully calculated woning waarde for eenheid: {eenheid_id}")
        
        return WoningwaarderingResponse(
            success=True,
            message="Woning waarde calculated successfully",
            eenheid_id=eenheid_id,
            peildatum=peildatum,
            detailed_json=json_output,
            table_output=table_output,
            raw_result=woningwaardering_resultaat
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=422, detail=f"Invalid input data: {str(e)}")
    except Exception as e:
        logger.error(f"Calculation error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Calculation failed: {str(e)}")


@app.post("/optimize")
async def find_optimization_suggestions(request: WoningwaarderingRequest) -> dict:
    """
    Analyze the housing unit and provide suggestions for improving the woning waarde score.
    
    This endpoint explores the solution space by:
    1. Identifying which scoring criteria could be improved
    2. Simulating changes to recommend the highest impact improvements
    3. Ranking suggestions by their potential score increase
    
    Returns a list of actionable suggestions with estimated score improvements.
    """
    try:
        # Parse the JSON input to EenhedenEenheid
        eenheid = EenhedenEenheid.model_validate(request.eenheid_data)
        
        # Use provided peildatum or default to today
        peildatum = request.peildatum or date.today()
        
        # Initialize Woningwaardering calculator
        wws = Woningwaardering(peildatum=peildatum)
        
        # Get baseline score
        baseline_result = wws.waardeer(eenheid)
        
        eenheid_id = getattr(eenheid, 'id', 'unknown')
        logger.info(f"Finding optimization opportunities for eenheid: {eenheid_id}")
        
        # Find optimization opportunities
        suggestions = find_optimization_opportunities(
            eenheid=eenheid,
            wws=wws,
            baseline_result=baseline_result,
            peildatum=peildatum
        )
        
        # Convert suggestions to dict if they're Pydantic models
        suggestions_list = []
        for s in suggestions:
            if hasattr(s, 'dict'):
                suggestions_list.append(s.dict())
            elif hasattr(s, 'model_dump'):
                suggestions_list.append(s.model_dump())
            else:
                suggestions_list.append(s)
        
        return {
            "success": True,
            "eenheid_id": eenheid_id,
            "suggestions": suggestions_list,
            "suggestion_count": len(suggestions_list)
        }
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=422, detail=f"Invalid input data: {str(e)}")
    except Exception as e:
        logger.error(f"Optimization error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Optimization analysis failed: {str(e)}")


@app.post("/batch-calculate")
async def batch_calculate(requests: List[WoningwaarderingRequest]) -> dict:
    """
    Calculate woning waarde for multiple housing units in batch.
    
    Returns results for all units, including any that failed with error messages.
    """
    results = []
    errors = []
    
    for idx, request in enumerate(requests):
        try:
            eenheid = EenhedenEenheid.model_validate(request.eenheid_data)
            peildatum = request.peildatum or date.today()
            
            # Create new calculator for each unit
            wws = Woningwaardering(peildatum=peildatum)
            woningwaardering_resultaat = wws.waardeer(eenheid)
            
            eenheid_id = getattr(eenheid, 'id', f'unit_{idx}')
            
            # Try to serialize the result
            try:
                result_data = woningwaardering_resultaat.model_dump(by_alias=True, exclude_none=True)
            except:
                result_data = str(woningwaardering_resultaat)
            
            results.append({
                "index": idx,
                "eenheid_id": eenheid_id,
                "success": True,
                "result": result_data
            })
        except Exception as e:
            logger.error(f"Batch calculation error at index {idx}: {str(e)}")
            errors.append({
                "index": idx,
                "error": str(e)
            })
    
    return {
        "total": len(requests),
        "successful": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
