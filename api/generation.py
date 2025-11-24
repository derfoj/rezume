# api/generation.py
import os
import logging
from typing import List, Any, Dict
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse

# --- Local Imports ---
from src.core.api_models import CVGenerationRequest
from src.agents.generator import GeneratorAgent
from src.core.knowledge_base import load_knowledge_base, Profile
from src.config.constants import KNOWLEDGE_BASE_PATH

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

@router.post("/generate-cv")
async def generate_cv_endpoint(request: CVGenerationRequest, background_tasks: BackgroundTasks):
    """
    Generates a PDF CV using the LLM-based Generator Agent and returns it for download.
    """
    try:
        # 1. Load and validate the user profile
        user_profile = load_knowledge_base(KNOWLEDGE_BASE_PATH)
        
        # 2. Instantiate the agent and generate the CV
        generator = GeneratorAgent()
        user_profile_dict = _profile_to_dict(user_profile)
        
        pdf_path, tex_path = generator.generate_cv_from_llm(
            user_profile=user_profile_dict,
            experiences=request.experiences
        )
        
        # 3. Schedule temporary files for cleanup (including the .tex file)
        cleanup_list = [tex_path, tex_path.replace(".tex", ".log"), tex_path.replace(".tex", ".aux")]
        background_tasks.add_task(cleanup_files, cleanup_list)

        # 4. Return the generated file for download
        return FileResponse(
            path=pdf_path,
            filename="reZume_CV_Generated.pdf",
            media_type='application/pdf',
            headers={"Content-Disposition": "attachment; filename=reZume_CV_Generated.pdf"}
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
