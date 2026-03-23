# api/generation.py
import os
import logging
import uuid
import json
from typing import List, Any, Dict, Optional
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
        {"id": "classic", "name": "Classique", "description": "Structure traditionnelle et efficace (sans photo).", "preview": "modern_preview.svg"}
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

def background_generate_cv(job_id: str, request: CVGenerationRequest, user_id: int, feedback: Optional[str] = None):
    """
    Worker function that generates the LaTeX source.
    The frontend handles compilation and 1-page validation.
    """
    db = SessionLocal()
    try:
        log_entry = db.query(UsageLog).filter(UsageLog.id == int(job_id)).first()
        if not log_entry: return

        user_profile = get_profile_from_db(db, user_id=user_id)
        current_user = db.query(User).filter(User.id == user_id).first()
        
        # 1. Ranking skills if needed
        if request.job_offer_text and user_profile.skills:
            try:
                user_profile.skills = _rank_skills_by_relevance(user_profile.skills, request.job_offer_text, top_n=15)
            except: pass
        
        generator = GeneratorAgent(
            provider=current_user.llm_provider,
            model=current_user.llm_model,
            api_key=current_user.openai_api_key if current_user.llm_provider == "openai" else None
        )
        
        logger.info(f"Generating LaTeX source for Job {job_id}")
        
        # Generator handles source generation and local file saving for audit
        latex_code = generator.generate_latex_source(
            user_profile=_profile_to_dict(user_profile),
            experiences=request.experiences,
            template_name=current_user.selected_template or "modern",
            feedback=feedback,
            session_id=job_id
        )
        
        # 3. Finalize
        log_entry.status = "success"
        log_entry.model = str(Path("outputs/generated_cvs") / job_id / f"cv_{job_id}.tex")
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
    
    background_tasks.add_task(background_generate_cv, str(log_entry.id), request, current_user.id, request.feedback)
    
    return {"job_id": str(log_entry.id), "message": "Génération de la source LaTeX lancée."}

@router.get("/status/{job_id}")
async def get_job_status(
    job_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    log = db.query(UsageLog).filter(UsageLog.id == int(job_id)).first()
    if not log:
        raise HTTPException(status_code=404, detail="Inconnu")
    
    # Ownership check
    if log.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès refusé.")
        
    return {"status": log.status, "progress": 100 if log.status == "success" else 50}

@router.get("/latex/{job_id}")
async def get_latex_source(
    job_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns the LaTeX source code for a generated CV.
    """
    log = db.query(UsageLog).filter(UsageLog.id == int(job_id)).first()
    if not log or log.status != "success":
        raise HTTPException(status_code=400, detail="CV non généré ou erreur.")
    
    # Ownership check
    if log.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès refusé.")
    
    tex_path = Path(log.model)
    if not tex_path.exists():
        raise HTTPException(status_code=404, detail="Source LaTeX introuvable.")
    
    with open(tex_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    return {"latex": content}
