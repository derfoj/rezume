# api/analysis.py
import logging
from fastapi import APIRouter, HTTPException

# --- Local Imports ---
from src.core.api_models import JobOfferRequest, AnalysisResponse
from src.core.orchestration import run_analysis_pipeline

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_endpoint(request: JobOfferRequest):
    """
    Analyzes a job offer and returns a structured analysis.
    This endpoint is a wrapper around the core analysis pipeline.
    """
    try:
        analysis_result = run_analysis_pipeline(request.raw_text)
        return AnalysisResponse(**analysis_result)
    except ValueError as e:
        # Catches business logic errors (e.g., empty text, parser failure)
        logger.warning(f"Validation error during analysis request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Catches unexpected server-side errors
        logger.error(f"An unhandled error occurred during analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected server error occurred during analysis.")
