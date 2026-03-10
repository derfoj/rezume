# api/analysis.py
import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from src.core.database import get_db
from pydantic import BaseModel

# --- Local Imports ---
from src.core.api_models import JobOfferRequest, AnalysisResponse
from src.core.orchestration import run_analysis_pipeline
from src.agents.optimizer import OptimizerAgent
from src.models.usage import UsageLog # New import

from src.api.auth import get_current_user
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
    # Log usage
    log_entry = UsageLog(
        user_id=current_user.id,
        action="job_analysis",
        provider=current_user.llm_provider or "openai",
        model=current_user.llm_model or "gpt-4o-mini",
        status="pending"
    )
    db.add(log_entry)
    db.commit()

    try:
        # Use the authenticated user's ID
        analysis_result = run_analysis_pipeline(request.raw_text, db=db, user_id=current_user.id)
        
        log_entry.status = "success"
        db.commit()
        
        return AnalysisResponse(**analysis_result)
    except ValueError as e:
        log_entry.status = "error"
        db.commit()
        logger.warning(f"Validation error during analysis request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log_entry.status = "error"
        db.commit()
        logger.error(f"An unhandled error occurred during analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected server error occurred during analysis.")

@router.post("/optimize-description")
def optimize_description_endpoint(
    request: OptimizationRequest,
    db: Session = Depends(get_db), # Added db for logging
    current_user: User = Depends(get_current_user)
):
    log_entry = UsageLog(
        user_id=current_user.id,
        action="text_optimization",
        provider=current_user.llm_provider or "openai",
        status="pending"
    )
    db.add(log_entry)
    db.commit()

    try:
        agent = OptimizerAgent()
        optimized_text = agent.optimize_description(request.text, tone=request.tone)
        
        log_entry.status = "success"
        db.commit()
        
        return {"optimized_text": optimized_text}
    except Exception as e:
        log_entry.status = "error"
        db.commit()
        logger.error(f"Optimization error: {e}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")
