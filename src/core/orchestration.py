# src/core/orchestration.py
import os
import logging
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
from thefuzz import process

from src.agents.parser import ParserAgent
from src.agents.optimizer import OptimizerAgent
from src.core.vector_store import search_vector_store, build_vector_store
from src.core.knowledge_base import get_profile_from_db
from sqlalchemy.orm import Session
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
        logger.info("Initializing ParserAgent...")
        parser_agent = ParserAgent(prompt_path="src/config/prompts/parser.yaml")
        logger.info("ParserAgent ready.")
    except Exception as e:
        logger.error(f"Failed to initialize ParserAgent: {e}", exc_info=True)
    
    return parser_agent

def initialize_optimizer_agent():
    """Initializes and returns the OptimizerAgent."""
    try:
        logger.info("Initializing OptimizerAgent...")
        return OptimizerAgent()
    except Exception as e:
        logger.error(f"Failed to initialize OptimizerAgent: {e}")
        return None

# Optimizer first, then Parser (LlamaIndex)
optimizer_agent = initialize_optimizer_agent()
parser_agent = initialize_parser_agent()

def _calculate_fuzzy_keyword_score(required_skills: list, user_skills: list) -> float:
    """
    Calculates a score based on fuzzy matching of required skills against the user's skill list.
    """
    if not required_skills or not user_skills:
        return 0.0

    found_count = 0
    user_skills_lower = {s.lower() for s in user_skills}

    for req_skill in required_skills:
        req_skill_lower = req_skill.lower()
        
        best_match, score = process.extractOne(req_skill_lower, user_skills_lower)
        
        if score > 85:
            found_count += 1

    return (found_count / len(required_skills)) * 100

def _cosine_similarity(v1, v2):
    """Calculates the cosine similarity between two vectors."""
    v1 = np.array(v1)
    v2 = np.array(v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0 # Or raise an error, depending on desired behavior
    return np.dot(v1, v2) / (norm_v1 * norm_v2)

def _diversify_results(
    results: list, 
    threshold: float = 0.95, 
    top_n: int = 3
) -> list:
    """
    Diversifies a list of search results based on embedding similarity
    to avoid returning overly similar experiences.
    """
    if not results:
        return []

    diverse_results = []
    
    for result in results:
        if len(diverse_results) >= top_n:
            break

        is_too_similar = False
        current_embedding_list = result.get('embedding')
        if current_embedding_list is None:
            logger.warning("Result missing embedding, skipping for diversification.")
            continue
        current_embedding = np.array(current_embedding_list)

        for diverse_res in diverse_results:
            diverse_embedding_list = diverse_res.get('embedding')
            if diverse_embedding_list is None:
                logger.warning("Diverse result missing embedding, skipping comparison.")
                continue
            diverse_embedding = np.array(diverse_embedding_list)
            
            similarity = _cosine_similarity(current_embedding, diverse_embedding)
            
            if similarity > threshold:
                is_too_similar = True
                logger.info(f"Skipping similar experience (similarity: {similarity:.2f})")
                break
        
        if not is_too_similar:
            diverse_results.append(result)
            
    return diverse_results

def _rank_skills_by_relevance(user_skills: list, offer_text: str, top_n: int = 15) -> list:
    """
    Ranks the user's skills based on their semantic relevance to the job offer text.
    """
    if not user_skills or not offer_text:
        return user_skills[:top_n]

    try:
        from src.core.vector_store import get_embedding, get_embeddings
        import numpy as np
        
        # Encode offer text (query)
        offer_embedding_list = get_embedding(f"query: {offer_text}")
        offer_embedding = np.array(offer_embedding_list, dtype=np.float32)
        norm_offer = np.linalg.norm(offer_embedding)
        
        # Encode skills (passages)
        skill_texts = [f"passage: {skill}" for skill in user_skills]
        skill_embeddings_list = get_embeddings(skill_texts)
        skill_embeddings = np.array(skill_embeddings_list, dtype=np.float32)
        
        # Calculate cosine similarity
        scores = []
        for i, skill_emb in enumerate(skill_embeddings):
            norm_skill = np.linalg.norm(skill_emb)
            if norm_offer == 0 or norm_skill == 0:
                score = 0
            else:
                score = np.dot(offer_embedding, skill_emb) / (norm_offer * norm_skill)
            scores.append((user_skills[i], score))
            
        # Sort by score descending
        ranked_skills = sorted(scores, key=lambda x: x[1], reverse=True)
        
        # Return top N skill names
        return [s[0] for s in ranked_skills[:top_n]]
        
    except ImportError:
        logger.warning("Could not import vector_store functions. Skipping skill ranking.")
        return user_skills[:top_n]
    except Exception as e:
        logger.warning(f"Skill ranking failed: {e}. Returning original order.")
        return user_skills[:top_n]
        
    except Exception as e:
        logger.warning(f"Skill ranking failed: {e}. Returning original order.")
        return user_skills[:top_n]

# --- ANALYSIS PIPELINE ---
def run_analysis_pipeline(raw_text: str, db: Session = None, user_id: int = 1) -> dict:
    """
    Runs the full analysis pipeline on a raw job offer text.
    """
    try:
        if not parser_agent:
            raise ValueError("AI service is not initialized.")

        if not raw_text or not raw_text.strip():
            raise ValueError("Job offer text cannot be empty.")

        logger.info(f"Starting analysis for job offer ({len(raw_text)} characters).")
        
        if not db:
            raise ValueError("Database session is required for analysis.")
            
        profile = get_profile_from_db(db, user_id)
        
        parsed = parser_agent.extract_information(raw_text)
        if not isinstance(parsed, dict) or "skills" not in parsed:
            raise ValueError("Failed to get structured data from the parsing agent.")

        skills_from_offer = parsed.get("skills", [])
        missions = parsed.get("missions", [])
        
        # --- NEW: Smart Skill Selection ---
        # Instead of just showing what the offer asks for, we show the user's best matching skills
        optimized_skills = _rank_skills_by_relevance(profile.skills, raw_text, top_n=12)
        
        query_str = f"Skills: {', '.join(skills_from_offer)}. Missions: {' '.join(missions)}"
        
        index_name = f"user_{user_id}"
        embedding_file = KNOWLEDGE_BASE_PATH.parent / "embeddings" / f"{index_name}.faiss"
        
        if not embedding_file.exists():
            logger.warning(f"Embedding index {index_name} not found. Building a new one for user {user_id}.")
            if profile and profile.experiences:
                # We need to construct documents with 'content' key as expected by build_vector_store
                # Reuse recalculate logic or simpler just for experiences here as a fallback?
                # Ideally we should call recalculate_user_embeddings but circular import risk or need DB session.
                # Let's do a simple fallback rebuild using the profile data we have.
                docs = []
                for exp in profile.experiences:
                    content = f"Experience: {exp.title} at {exp.company} ({exp.period}). {exp.description}"
                    docs.append({"content": content, "metadata": exp.__dict__, "type": "experience"})
                
                build_vector_store(docs, index_name)
        
        initial_matches = search_vector_store(query_str, index_name=index_name, top_n=20)
        
        # Filter only for experiences to avoid matching education/skills here
        experience_matches = [m for m in initial_matches if m.get('type') == 'experience']
        
        matches = _diversify_results(experience_matches, top_n=3)

        # --- FALLBACK: KEYWORD MATCHING IF SEMANTIC SEARCH IS WEAK ---
        if not matches and profile.experiences:
            logger.info("Semantic search yielded no results. Attempting keyword-based fallback...")
            fallback_matches = []
            for exp in profile.experiences:
                # Count matching skills in title/description
                content_lower = f"{exp.title} {exp.description}".lower()
                match_count = sum(1 for skill in skills_from_offer if skill.lower() in content_lower)
                
                if match_count > 0:
                    fallback_matches.append({
                        "title": exp.title,
                        "company": exp.company,
                        "period": exp.period,
                        "description": exp.description,
                        "keyword_score": match_count
                    })
            
            # Sort by match count and take top 3
            fallback_matches = sorted(fallback_matches, key=lambda x: x['keyword_score'], reverse=True)[:3]
            if fallback_matches:
                logger.info(f"Found {len(fallback_matches)} experiences via keyword fallback.")
                matches = fallback_matches

        bullet_points = []
        final_score = 0
        
        keyword_score = _calculate_fuzzy_keyword_score(skills_from_offer, profile.skills)

        if matches:
            # Calculate semantic score (use keyword_score if semantic vector scores are missing)
            vector_scores = [m.get('match_score', 0) for m in matches if 'match_score' in m]
            semantic_score = (sum(vector_scores) / len(vector_scores)) * 100 if vector_scores else 20 # Low default if fallback
            
            weighted_score = (semantic_score * 0.6) + (keyword_score * 0.4)
            final_score = max(0, min(100, int(weighted_score)))

            for m in matches:
                m.pop('embedding', None)
                m.pop('keyword_score', None)
                
                # --- NEW: Ensure metadata fields are at top level for frontend ---
                if 'metadata' in m:
                    for key, val in m['metadata'].items():
                        if key not in m:
                            m[key] = val

                # --- NEW: LLM-based optimization for each experience ---
                try:
                    original_desc = m.get('description', '')
                    # We optimize the description specifically for this job offer
                    # SANITIZED CONTEXT: We pass only skills and missions to avoid hallucinating the company name
                    sanitized_context = f"Compétences recherchées: {', '.join(skills_from_offer)}. Missions: {' '.join(missions)}"
                    
                    if optimizer_agent:
                        optimized_desc = optimizer_agent.optimize_description(
                            original_desc, 
                            job_offer=sanitized_context
                        )
                        m['description'] = optimized_desc
                    else:
                        optimized_desc = original_desc

                    # Create a summary bullet point for display
                    bullet_points.append(f"{m.get('title')}: {optimized_desc.split('.')[0]}...")
                except Exception as e:
                    logger.warning(f"Failed to optimize description for {m.get('title')}: {e}")
                    # Fallback to original excerpt logic
                    description = m.get('description', '')
                    bullet_points.append(f"{m.get('title')}: {description.split('.')[0]}...")
        else:
            final_score = max(0, min(100, int(keyword_score)))
            bullet_points = ["Nous n'avons pas trouvé d'expérience correspondant exactement à cette offre dans votre historique, mais vos compétences semblent alignées. C'est peut-être l'occasion de mettre en avant vos projets personnels ou votre capacité d'apprentissage !"]

        summary_text = f"Profile match: {final_score}% based on a hybrid analysis of semantic experience relevance and direct skill matching."
        
        logger.info(f"Analysis complete. Final score: {final_score}")

        return {
            "score": final_score,
            "summary": summary_text,
            "skills": optimized_skills, # Returning user's relevant skills instead of offer's required skills
            "bulletPoints": bullet_points,
            "raw_matches": matches
        }
    except ValueError as ve:
        logger.error(f"Validation error in analysis pipeline: {ve}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred in the analysis pipeline: {e}", exc_info=True)
        raise ValueError("An unexpected error occurred during analysis.")

