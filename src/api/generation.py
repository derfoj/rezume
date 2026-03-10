# api/generation.py
import os
import logging
from typing import List, Any, Dict
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from src.core.database import get_db

# --- Local Imports ---
from src.core.api_models import CVGenerationRequest
from src.agents.generator import GeneratorAgent
from src.core.knowledge_base import get_profile_from_db, Profile
from src.api.auth import get_current_user
from src.models.user import User
from src.config.constants import TEMPLATES_DIR
from src.core.orchestration import _rank_skills_by_relevance # Réintégration de la fonction de base
import json
import urllib.parse
from pathlib import Path

router = APIRouter()
logger = logging.getLogger(__name__)

def _profile_to_dict(profile: Profile) -> Dict[str, Any]:
    """Converts Profile to a JSON-safe dictionary with type safety."""
    def to_dict(obj):
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        if isinstance(obj, dict):
            return obj
        return str(obj)

    return {
        "name": profile.name,
        "title": profile.title,
        "summary": profile.summary,
        "email": profile.email,
        "portfolio_url": profile.portfolio_url,
        "linkedin_url": profile.linkedin_url,
        "photo_path": profile.photo_path,
        "skills": profile.skills,
        "soft_skills": profile.soft_skills,
        "experiences": [to_dict(exp) for exp in profile.experiences],
        "education": [to_dict(edu) for edu in profile.education],
        "languages": [to_dict(lang) for lang in profile.languages],
    }

@router.get("/templates")
def get_templates():
    metadata_path = TEMPLATES_DIR / "metadata.json"
    if metadata_path.exists():
        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

@router.post("/generate-cv")
async def generate_cv_endpoint(
    request: CVGenerationRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # 1. Charger le profil utilisateur
        user_profile = get_profile_from_db(db, user_id=current_user.id)
        
        # 2. APPLICATION DU TRI INTELLIGENT (Base de la plateforme)
        # Si une offre d'emploi est fournie, on trie les compétences par pertinence
        if request.job_offer_text and user_profile.skills:
            try:
                logger.info("Tri intelligent des compétences en cours...")
                relevant_skills = _rank_skills_by_relevance(user_profile.skills, request.job_offer_text, top_n=15)
                user_profile.skills = relevant_skills
            except Exception as e:
                logger.warning(f"Le tri intelligent a échoué ({e}), utilisation de l'ordre par défaut.")
        
        # 3. Configurer l'agent de génération
        generator = GeneratorAgent(
            provider=current_user.llm_provider or "openai",
            model=current_user.llm_model or "gpt-4o-mini",
            api_key=current_user.openai_api_key if current_user.llm_provider == "openai" else None
        )
        
        # 4. Générer le CV
        # On convertit le profil en dict sécurisé pour l'IA
        profile_dict = _profile_to_dict(user_profile)
        
        pdf_path, tex_path = generator.generate_cv_from_llm(
            user_profile=profile_dict,
            experiences=request.experiences,
            template_name=current_user.selected_template or "modern"
        )
        
        # 5. Retourner le fichier
        return FileResponse(
            path=pdf_path,
            filename="reZume_CV_Optimise.pdf",
            media_type='application/pdf',
            headers={"X-Generation-ID": Path(pdf_path).parent.name}
        )
        
    except Exception as e:
        logger.error(f"Échec de la génération du CV : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur interne lors de la génération : {str(e)}")
