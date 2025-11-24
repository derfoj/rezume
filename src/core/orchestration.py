# src/core/orchestration.py
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

from src.agents.parser import ParserAgent
from src.core.vector_store import search_vector_store, build_vector_store
from src.core.knowledge_base import load_knowledge_base
from src.config.constants import KNOWLEDGE_BASE_PATH

# Configure logging for this module
logger = logging.getLogger(__name__)

# --- AGENT INITIALIZATION ---
def initialize_parser_agent():
    """Initializes and returns the ParserAgent if API key is available."""
    base_dir = Path(__file__).resolve().parent.parent.parent
    env_path = base_dir / ".env"
    load_dotenv(dotenv_path=env_path)
    
    parser_agent = None
    try:
        # The ParserAgent's __init__ will handle the logic of checking keys 
        # and availability of the LLM.
        logger.info("Initializing ParserAgent...")
        parser_agent = ParserAgent(prompt_path="src/config/prompts/parser.yaml")
        logger.info("ParserAgent ready.")
    except Exception as e:
        logger.error(f"Failed to initialize ParserAgent: {e}", exc_info=True)
    
    return parser_agent

parser_agent = initialize_parser_agent()

def _calculate_keyword_score(required_skills: list, experiences: list) -> float:
    """Calculates a score based on the percentage of required skills found in experiences."""
    if not required_skills or not experiences:
        return 0.0

    found_skills = set()
    experience_text = " ".join([
        f"{exp.get('title', '')} {exp.get('description', '')}" 
        for exp in experiences
    ]).lower()

    for skill in required_skills:
        if skill.lower() in experience_text:
            found_skills.add(skill.lower())
    
    return (len(found_skills) / len(required_skills)) * 100

# --- ANALYSIS PIPELINE ---
def run_analysis_pipeline(raw_text: str) -> dict:
    """
    Runs the full analysis pipeline on a raw job offer text.
    """
    try:
        if not parser_agent:
            raise ValueError("AI service is not initialized.")

        if not raw_text or not raw_text.strip():
            raise ValueError("Job offer text cannot be empty.")

        logger.info(f"Starting analysis for job offer ({len(raw_text)} characters).")
        
        # 1. Extraction from text
        parsed = parser_agent.extract_information(raw_text)
        if not isinstance(parsed, dict) or "skills" not in parsed:
            raise ValueError("Failed to get structured data from the parsing agent.")

        skills_from_offer = parsed.get("skills", [])
        missions = parsed.get("missions", [])
        
        # 2. Vector Search
        query_str = f"Skills: {', '.join(skills_from_offer)}. Missions: {' '.join(missions)}"
        
        embedding_file = Path("data/embeddings/kb_index.faiss")
        if not embedding_file.exists():
            logger.warning("Embedding index not found. Building a new one.")
            profile = load_knowledge_base()
            if profile and profile.experiences:
                experiences_as_dicts = [exp.__dict__ for exp in profile.experiences]
                build_vector_store(experiences_as_dicts, "kb_index")
        
        matches = search_vector_store(query_str, index_name="kb_index", top_n=3)

        # 3. Hybrid Scoring and Formatting
        bullet_points = []
        final_score = 0

        if matches:
            vector_scores = [m.get('match_score', 0) for m in matches]
            avg_vector_score = sum(vector_scores) / len(vector_scores) if vector_scores else 0
            keyword_score = _calculate_keyword_score(skills_from_offer, matches)
            weighted_score = (avg_vector_score * 100 * 0.6) + (keyword_score * 0.4)
            final_score = max(0, min(100, int(weighted_score)))

            for m in matches:
                desc = m.get('description', '').split('.')[0]
                bullet_points.append(f"{m.get('title')}: {desc}...")
        else:
            bullet_points = ["No relevant experiences found in the knowledge base."]

        summary_text = f"Profile match: {final_score}% based on hybrid analysis."
        
        logger.info(f"Analysis complete. Final score: {final_score}")

        return {
            "score": final_score,
            "summary": summary_text,
            "skills": skills_from_offer[:10],
            "bulletPoints": bullet_points,
            "raw_matches": matches
        }
    except ValueError as ve:
        logger.error(f"Validation error in analysis pipeline: {ve}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred in the analysis pipeline: {e}", exc_info=True)
        raise ValueError("An unexpected error occurred during analysis.")
