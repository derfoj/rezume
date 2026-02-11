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
from src.api.profile import get_current_user
from src.models.user import User
from src.config.constants import TEMPLATES_DIR
import json

router = APIRouter()
logger = logging.getLogger(__name__)

# --- Helper Functions ---
def cleanup_files(file_paths: List[str]):
    """Removes temporary files in the background."""
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
                logger.info(f"Successfully cleaned up temporary file: {path}")
        except Exception as e:
            logger.warning(f"Failed to clean up temporary file {path}: {e}")

def _profile_to_dict(profile: Profile) -> Dict[str, Any]:
    """
    Converts a Profile object and its nested dataclasses into a dictionary
    that is safe for JSON serialization.
    """
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
        "experiences": [exp.__dict__ for exp in profile.experiences],
        "education": [edu.__dict__ for edu in profile.education],
        "languages": [lang.__dict__ for lang in profile.languages],
    }

@router.get("/templates")
def get_templates():
    """Returns the list of available CV templates."""
    metadata_path = TEMPLATES_DIR / "metadata.json"
    if metadata_path.exists():
        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

from pathlib import Path
from src.core.cv_validator import validate_cv
import urllib.parse

@router.post("/generate-cv")
async def generate_cv_endpoint(
    request: CVGenerationRequest, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generates a PDF CV using the LLM-based Generator Agent and returns it for download.
    Includes an auto-correction loop to ensure compliance (max 2 retries).
    """
    try:
        # 1. Load and validate the user profile
        user_profile = get_profile_from_db(db, user_id=current_user.id)
        
        # 2. Instantiate the agent
        generator = GeneratorAgent(
            provider=current_user.llm_provider,
            model=current_user.llm_model,
            api_key=current_user.openai_api_key if current_user.llm_provider == "openai" else None 
        )
        user_profile_dict = _profile_to_dict(user_profile)
        
        # Initial Generation
        pdf_path, tex_path = generator.generate_cv_from_llm(
            user_profile=user_profile_dict,
            experiences=request.experiences,
            template_name=current_user.selected_template or "classic"
        )
        
        # Auto-correction Loop
        MAX_RETRIES = 2
        attempt = 0
        
        while attempt < MAX_RETRIES:
            validation_result = validate_cv(tex_path)
            
            if validation_result["valid"]:
                logger.info("CV validation passed on attempt %d.", attempt + 1)
                break
            
            # Construct feedback from warnings
            warnings = validation_result.get("warnings", [])
            feedback_intro = "URGENT : LE CV GÉNÉRÉ EST INVALIDE."
            feedback_details = "\n".join(warnings)
            feedback_action = "Tu DOIS corriger ces erreurs MAINTENANT. Si le problème est la longueur (plus d'une page), SOIS RADICAL : supprime les expériences les plus anciennes, réduis les descriptions à 1-2 puces maximum, ou supprime le résumé. Il vaut mieux un CV incomplet qui tient sur 1 page qu'un CV trop long."
            
            feedback = f"{feedback_intro}\nProblèmes détectés :\n{feedback_details}\n\nINSTRUCTION DE CORRECTION :\n{feedback_action}"
            
            logger.warning(f"CV validation failed on attempt {attempt + 1}. Retrying with feedback: {feedback}")
            
            # Retry generation with feedback using the SAME session directory
            session_dir = Path(tex_path).parent
            pdf_path, tex_path = generator.generate_cv_from_llm(
                user_profile=user_profile_dict,
                experiences=request.experiences,
                template_name=current_user.selected_template or "classic",
                feedback=feedback,
                session_dir=session_dir
            )
            attempt += 1
        
        # Final validation check (to populate headers correctly)
        validation_result = validate_cv(tex_path)
        
        # Encode validation result for header
        validation_header = urllib.parse.quote(json.dumps(validation_result))

        # 4. Return the generated file for download with validation headers
        return FileResponse(
            path=pdf_path,
            filename="reZume_CV_Generated.pdf",
            media_type='application/pdf',
            headers={
                "Content-Disposition": "attachment; filename=reZume_CV_Generated.pdf",
                "X-CV-Validation-Report": validation_header
            }
        )
    except (FileNotFoundError, ValueError) as e:
        # Catches issues like a missing knowledge base or JSON schema validation errors.
        logger.warning(f"Failed to generate CV due to data validation issues: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to process knowledge base: {e}")
    except RuntimeError as e:
        # Catches errors from the generator agent (e.g., LLM call or LaTeX compilation failure).
        logger.error(f"A runtime error occurred during CV generation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {e}")
    except Exception as e:
        # Catches any other unexpected server-side errors.
        logger.critical(f"An unexpected critical error occurred during CV generation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred: {e}")
