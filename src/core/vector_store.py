import faiss
import numpy as np
import os
import json
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from src.config.constants import EMBEDDINGS_DIR
from sqlalchemy.orm import Session
from src.core.knowledge_base import get_profile_from_db
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Use a consistent model for generating embeddings
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
# Load model globally to avoid reloading on every call (caching strategy)
_model_instance = None

def get_model():
    global _model_instance
    if _model_instance is None:
        # Force CPU usage to avoid potential 'meta' tensor issues on some configs
        _model_instance = SentenceTransformer(MODEL_NAME, device="cpu")
    return _model_instance

def build_vector_store(documents: List[Dict[str, Any]], index_name: str = "kb_index"):
    """
    Builds and saves a FAISS index using cosine similarity (Inner Product).
    
    Args:
        documents: List of dicts. Each dict MUST have a 'content' key (text to embed).
                   Other keys are stored as metadata.
        index_name: Name of the index file (e.g. 'user_123').
    """
    if not documents:
        logger.warning(f"No documents provided to build vector store for {index_name}.")
        return

    os.makedirs(EMBEDDINGS_DIR, exist_ok=True)
    
    index_path = os.path.join(EMBEDDINGS_DIR, f"{index_name}.faiss")
    data_path = os.path.join(EMBEDDINGS_DIR, f"{index_name}.json")

    # Extract text content
    texts = [doc.get('content', '') for doc in documents]
    
    # Generate embeddings
    model = get_model()
    logger.info(f"Generating embeddings for {len(texts)} documents ({index_name})...")
    embeddings = model.encode(texts, convert_to_tensor=False, show_progress_bar=False)
    embeddings = np.array(embeddings, dtype=np.float32)
    
    # Normalize for Cosine Similarity
    faiss.normalize_L2(embeddings)

    # Build Index
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    
    # Save Index
    faiss.write_index(index, index_path)
    
    # Save Metadata (original docs + implicit order)
    # We don't save the raw vectors in JSON to save space, but we could if needed.
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(documents, f, ensure_ascii=False, indent=4)
        
    logger.info(f"Index built and saved to {index_path}")

def recalculate_user_embeddings(user_id: int, db: Session):
    """
    Fetches the user's full profile (Experiences, Skills, etc.), 
    formats them into documents, and rebuilds their personal vector index.
    """
    try:
        logger.info(f"Recalculating embeddings for User {user_id}...")
        profile = get_profile_from_db(db, user_id)
        
        documents = []
        
        # 1. Experiences
        for exp in profile.experiences:
            content = f"Experience: {exp.title} at {exp.company} ({exp.period}). {exp.description}"
            documents.append({
                "type": "experience",
                "content": content,
                "metadata": {
                    "title": exp.title,
                    "company": exp.company,
                    "period": exp.period
                }
            })
            
        # 2. Education
        for edu in profile.education:
            content = f"Education: {edu.degree} at {edu.institution} ({edu.period})."
            documents.append({
                "type": "education",
                "content": content,
                "metadata": {
                    "institution": edu.institution,
                    "degree": edu.degree
                }
            })

        # 3. Skills (Grouped or individual)
        # Embedding individual skills might be noisy, but good for keyword matching.
        # Let's chunk them a bit or just list them.
        if profile.skills:
            content = f"Technical Skills: {', '.join(profile.skills)}"
            documents.append({
                "type": "skills_hard",
                "content": content,
                 "metadata": {"skills": profile.skills}
            })
            
        if profile.soft_skills:
            content = f"Soft Skills: {', '.join(profile.soft_skills)}"
            documents.append({
                "type": "skills_soft",
                "content": content,
                "metadata": {"skills": profile.soft_skills}
            })
        
        # 4. Summary/Bio
        if profile.summary:
            documents.append({
                "type": "summary",
                "content": f"Professional Summary: {profile.summary}",
                "metadata": {}
            })

        # Build the index specific to this user
        build_vector_store(documents, index_name=f"user_{user_id}")
        logger.info(f"Successfully updated embeddings for User {user_id}")
        
    except Exception as e:
        logger.error(f"Failed to recalculate embeddings for User {user_id}: {e}")
        # Build an empty index or handle error gracefully?
        # For now, we just log it.

def search_vector_store(
    query_text: str, 
    index_name: str = "kb_index", 
    top_n: int = 3
) -> List[Dict[str, Any]]:
    """
    Searches a FAISS index using cosine similarity.
    """
    index_path = os.path.join(EMBEDDINGS_DIR, f"{index_name}.faiss")
    data_path = os.path.join(EMBEDDINGS_DIR, f"{index_name}.json")

    if not os.path.exists(index_path) or not os.path.exists(data_path):
        logger.warning(f"Index '{index_name}' not found. Returning empty results.")
        return []

    # Load resources
    index = faiss.read_index(index_path)
    with open(data_path, 'r', encoding='utf-8') as f:
        documents = json.load(f)

    # Encode Query
    model = get_model()
    query_embedding = model.encode([query_text])
    query_embedding = np.array(query_embedding, dtype=np.float32)
    faiss.normalize_L2(query_embedding)

    # Search
    # Check if we have enough documents
    k = min(top_n, index.ntotal)
    if k == 0:
        return []
        
    distances, indices = index.search(query_embedding, k)

    # Format Results
    results = []
    for i, idx in enumerate(indices[0]):
        if idx != -1:
            doc = documents[idx]
            doc['match_score'] = float(distances[0][i])
            results.append(doc)
            
    return results
