# api/analysis.py
import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from src.core.database import get_db
from pydantic import BaseModel

# --- Local Imports ---
from src.core.api_models import JobOfferRequest, AnalysisResponse
from src.core.orchestration import run_analysis_pipeline
from src.agents.optimizer import OptimizerAgent # New import

from src.api.profile import get_current_user
from src.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)

class OptimizationRequest(BaseModel):
    text: str
    tone: str = "standard"

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_endpoint(
    request: JobOfferRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyzes a job offer and returns a structured analysis.
    This endpoint is a wrapper around the core analysis pipeline.
    """
    try:
        # Use the authenticated user's ID
        analysis_result = run_analysis_pipeline(request.raw_text, db=db, user_id=current_user.id)
        return AnalysisResponse(**analysis_result)
    except ValueError as e:
        # Catches business logic errors (e.g., empty text, parser failure)
        logger.warning(f"Validation error during analysis request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Catches unexpected server-side errors
        logger.error(f"An unhandled error occurred during analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected server error occurred during analysis.")

@router.post("/optimize-description")
def optimize_description_endpoint(
    request: OptimizationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Optimizes a job description using the STAR method with a specific tone.
    """
    try:
        agent = OptimizerAgent()
        optimized_text = agent.optimize_description(request.text, tone=request.tone)
        return {"optimized_text": optimized_text}
    except Exception as e:
        logger.error(f"Optimization error: {e}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")
