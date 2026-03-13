# api/generation.py
import os
import logging
import uuid
import json
from typing import List, Any, Dict
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from src.core.database import get_db, SessionLocal
from pathlib import Path

# --- Local Imports ---
from src.core.api_models import CVGenerationRequest
from src.agents.generator import GeneratorAgent
from src.core.knowledge_base import get_profile_from_db, Profile
from src.api.auth import get_current_user
from src.models.user import User
from src.models.usage import UsageLog
from src.config.constants import TEMPLATES_DIR
from src.core.orchestration import _rank_skills_by_relevance
from src.core.cv_validator import validate_cv

router = APIRouter()
logger = logging.getLogger(__name__)

def _profile_to_dict(profile: Profile) -> Dict[str, Any]:
    def to_dict(obj):
        return obj.__dict__ if hasattr(obj, "__dict__") else str(obj)
    return {
        "name": profile.name, "title": profile.title, "summary": profile.summary,
        "email": profile.email, "portfolio_url": profile.portfolio_url,
        "linkedin_url": profile.linkedin_url, "photo_path": profile.photo_path,
        "skills": profile.skills, "soft_skills": profile.soft_skills,
        "experiences": [to_dict(exp) for exp in profile.experiences],
        "education": [to_dict(edu) for edu in profile.education],
        "languages": [to_dict(lang) for lang in profile.languages],
    }

def background_generate_cv(job_id: str, request: CVGenerationRequest, user_id: int):
    """
    Worker function using DB for persistence. Survival mode for Render Free.
    """
    db = SessionLocal()
    try:
        # Update progress in DB (using model column instead of in-memory)
        log_entry = db.query(UsageLog).filter(UsageLog.id == int(job_id)).first()
        if not log_entry: return

        user_profile = get_profile_from_db(db, user_id=user_id)
        current_user = db.query(User).filter(User.id == user_id).first()
        
        # 1. Ranking
        if request.job_offer_text and user_profile.skills:
            try:
                user_profile.skills = _rank_skills_by_relevance(user_profile.skills, request.job_offer_text, top_n=15)
            except: pass
        
        # 2. Generation
        generator = GeneratorAgent(
            provider=current_user.llm_provider,
            model=current_user.llm_model,
            api_key=current_user.openai_api_key if current_user.llm_provider == "openai" else None
        )
        
        pdf_path, tex_path = generator.generate_cv_from_llm(
            user_profile=_profile_to_dict(user_profile),
            experiences=request.experiences,
            template_name=current_user.selected_template or "modern"
        )
        
        # 3. Finalize
        log_entry.status = "success"
        log_entry.model = pdf_path # Temporary hijack model column to store path
        db.commit()

    except Exception as e:
        logger.error(f"Background Generation Failed: {e}")
        log_entry = db.query(UsageLog).filter(UsageLog.id == int(job_id)).first()
        if log_entry:
            log_entry.status = "error"
            db.commit()
    finally:
        db.close()

@router.post("/generate-cv")
async def generate_cv_endpoint(
    request: CVGenerationRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Create persistent DB log
    log_entry = UsageLog(
        user_id=current_user.id,
        action="cv_generation",
        status="processing"
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    
    background_tasks.add_task(background_generate_cv, str(log_entry.id), request, current_user.id)
    
    return {"job_id": str(log_entry.id), "message": "Génération lancée."}

@router.get("/status/{job_id}")
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    log = db.query(UsageLog).filter(UsageLog.id == int(job_id)).first()
    if not log:
        raise HTTPException(status_code=404, detail="Inconnu")
    return {"status": log.status, "progress": 100 if log.status == "success" else 50}

@router.get("/download/{job_id}")
async def download_cv(job_id: str, db: Session = Depends(get_db)):
    log = db.query(UsageLog).filter(UsageLog.id == int(job_id)).first()
    if not log or log.status != "success":
        raise HTTPException(status_code=400, detail="Non prêt")
    
    return FileResponse(
        path=log.model, # Path stored during generation
        filename="reZume_CV.pdf",
        media_type='application/pdf'
    )
