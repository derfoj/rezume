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

# In-memory storage for job status (for faster polling than DB)
# In production with multiple workers, you'd use Redis, but for Render Free -w 1, this works perfectly.
jobs_status = {}

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
    Worker function running in background to handle heavy LLM + LaTeX tasks.
    """
    db = SessionLocal()
    try:
        jobs_status[job_id] = {"status": "processing", "progress": 20}
        
        current_user = db.query(User).filter(User.id == user_id).first()
        user_profile = get_profile_from_db(db, user_id=user_id)
        
        # 1. Ranking
        if request.job_offer_text and user_profile.skills:
            jobs_status[job_id]["progress"] = 40
            try:
                user_profile.skills = _rank_skills_by_relevance(user_profile.skills, request.job_offer_text, top_n=15)
            except: pass
        
        # 2. Generation
        jobs_status[job_id]["progress"] = 60
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
        
        # 3. Validation
        jobs_status[job_id]["progress"] = 90
        validation = validate_cv(tex_path)
        if not validation["valid"]:
            # One retry if needed
            pdf_path, tex_path = generator.generate_cv_from_llm(
                user_profile=_profile_to_dict(user_profile),
                experiences=request.experiences,
                template_name=current_user.selected_template or "modern",
                feedback="RÉDUIRE LA LONGUEUR : Le CV dépasse une page."
            )

        # Mark as finished
        jobs_status[job_id] = {
            "status": "completed", 
            "progress": 100, 
            "pdf_path": pdf_path,
            "generation_id": Path(pdf_path).parent.name
        }
        
        # Log success
        db.add(UsageLog(user_id=user_id, action="cv_generation", status="success"))
        db.commit()

    except Exception as e:
        logger.error(f"Background Generation Failed: {e}")
        jobs_status[job_id] = {"status": "failed", "error": str(e)}
        db.add(UsageLog(user_id=user_id, action="cv_generation", status="error"))
        db.commit()
    finally:
        db.close()

@router.post("/generate-cv")
async def generate_cv_endpoint(
    request: CVGenerationRequest, 
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Starts the generation process and returns a job_id immediately."""
    job_id = str(uuid.uuid4())
    jobs_status[job_id] = {"status": "pending", "progress": 0}
    
    background_tasks.add_task(background_generate_cv, job_id, request, current_user.id)
    
    return {"job_id": job_id, "message": "Génération lancée en arrière-plan."}

@router.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """Endpoint for the frontend to poll status."""
    if job_id not in jobs_status:
        raise HTTPException(status_code=404, detail="Job non trouvé.")
    return jobs_status[job_id]

@router.get("/download/{job_id}")
async def download_cv(job_id: str):
    """Endpoint to download the final file once completed."""
    job = jobs_status.get(job_id)
    if not job or job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Fichier non prêt.")
    
    return FileResponse(
        path=job["pdf_path"],
        filename="reZume_CV.pdf",
        media_type='application/pdf',
        headers={"X-Generation-ID": job["generation_id"]}
    )
