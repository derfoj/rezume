# src/core/api_models.py
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class JobOfferRequest(BaseModel):
    """Request model for the analysis endpoint."""
    raw_text: str

class AnalysisResponse(BaseModel):
    """Response model for the analysis endpoint."""
    score: int
    summary: str
    skills: List[str]
    bulletPoints: List[str]
    raw_matches: List[Dict[str, Any]]

class CVGenerationRequest(BaseModel):
    """Request model for the CV generation endpoint."""
    experiences: List[Dict[str, Any]]
    job_offer_text: Optional[str] = None
    generation_id: Optional[str] = None
