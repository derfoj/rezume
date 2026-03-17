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

# --- ENDPOINTS ---

@router.get("/templates")
async def get_templates():
    """
    Returns the list of available CV templates.
    """
    templates = [
        {"id": "modern", "name": "Moderne", "description": "Design épuré et professionnel.", "preview": "modern_preview.svg"},
        {"id": "photo_header", "name": "Avec Photo", "description": "Mise en avant de votre profil avec photo.", "preview": "photo_preview.svg"},
        {"id": "classic", "name": "Classique", "description": "Structure traditionnelle et efficace (sans photo).", "preview": "modern_preview.svg"} # Use modern as fallback if classic preview is missing
    ]
    return templates


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
    Worker function with retry logic for 1-page constraint.
    """
    db = SessionLocal()
    try:
        log_entry = db.query(UsageLog).filter(UsageLog.id == int(job_id)).first()
        if not log_entry: return

        user_profile = get_profile_from_db(db, user_id=user_id)
        current_user = db.query(User).filter(User.id == user_id).first()
        
        # 1. Ranking skills
        if request.job_offer_text and user_profile.skills:
            try:
                user_profile.skills = _rank_skills_by_relevance(user_profile.skills, request.job_offer_text, top_n=15)
            except: pass
        
        generator = GeneratorAgent(
            provider=current_user.llm_provider,
            model=current_user.llm_model,
            api_key=current_user.openai_api_key if current_user.llm_provider == "openai" else None
        )
        
        # Retry loop for 1-page constraint
        max_retries = 2
        pdf_path, tex_path = None, None
        
        for attempt in range(max_retries):
            logger.info(f"Generation attempt {attempt + 1} for Job {job_id}")
            
            # On second attempt, force extreme conciseness
            feedback = None
            if attempt > 0:
                feedback = "Le CV précédent était trop long (plus d'une page). RESTE SUR UNE SEULE PAGE. Sois très concis, élimine le superflu."

            pdf_path, tex_path = generator.generate_cv_from_llm(
                user_profile=_profile_to_dict(user_profile),
                experiences=request.experiences,
                template_name=current_user.selected_template or "modern",
                feedback=feedback
            )
            
            # Validate page count
            validation = validate_cv(tex_path)
            if validation["valid"]:
                logger.info(f"✅ CV validated (1 page) on attempt {attempt + 1}")
                break
            else:
                logger.warning(f"⚠️ CV validation failed: {validation['warnings']}")
                if attempt == max_retries - 1:
                    raise RuntimeError(f"Impossible de générer un CV sur une seule page après {max_retries} tentatives.")

        # 3. Finalize
        log_entry.status = "success"
        log_entry.model = pdf_path
        db.commit()

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"❌ Background Generation Failed for Job {job_id}: {e}\n{error_details}")
        log_entry = db.query(UsageLog).filter(UsageLog.id == int(job_id)).first()
        if log_entry:
            log_entry.status = "error"
            log_entry.model = f"Error: {str(e)[:100]}"
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
async def download_cv(job_id: str, inline: bool = False, db: Session = Depends(get_db)):
    log = db.query(UsageLog).filter(UsageLog.id == int(job_id)).first()
    if not log or log.status != "success":
        raise HTTPException(status_code=400, detail="Non prêt")
    
    headers = {}
    if inline:
        # 'inline' tells the browser to try and show the file inside the page
        headers["Content-Disposition"] = "inline"
    
    return FileResponse(
        path=log.model, 
        filename="reZume_CV.pdf" if not inline else None,
        media_type='application/pdf',
        headers=headers
    )
