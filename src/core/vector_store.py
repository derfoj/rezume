import faiss
import numpy as np
import os
import json
from typing import List, Dict, Any
from openai import OpenAI
from src.config.constants import EMBEDDINGS_DIR
from sqlalchemy.orm import Session
from src.core.knowledge_base import get_profile_from_db
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Use OpenAI's efficient embedding model
MODEL_NAME = "text-embedding-3-small"

def get_embedding(text: str) -> List[float]:
    """
    Generates an embedding for a given text using OpenAI API.
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    text = text.replace("\n", " ")  # Normalize newlines
    try:
        return client.embeddings.create(input=[text], model=MODEL_NAME).data[0].embedding
    except Exception as e:
        logger.error(f"Error generating embedding with OpenAI: {e}")
        # Return a zero vector of appropriate size (1536 for text-embedding-3-small) as fallback
        return [0.0] * 1536

def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generates embeddings for a list of texts using OpenAI API.
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    # Normalize newlines
    texts = [t.replace("\n", " ") for t in texts]
    try:
        response = client.embeddings.create(input=texts, model=MODEL_NAME)
        return [data.embedding for data in response.data]
    except Exception as e:
        logger.error(f"Error generating embeddings with OpenAI: {e}")
        return [[0.0] * 1536 for _ in texts]

def build_vector_store(documents: List[Dict[str, Any]], index_name: str = "kb_index"):
    """
    Builds and saves a FAISS index using cosine similarity.
    
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
    
    # Generate embeddings via API
    logger.info(f"Generating OpenAI embeddings for {len(texts)} documents ({index_name})...")
    embeddings_list = get_embeddings(texts)
    embeddings = np.array(embeddings_list, dtype=np.float32)
    
    # Normalize for Cosine Similarity (OpenAI embeddings are usually normalized, but good practice)
    faiss.normalize_L2(embeddings)

    # Build Index
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    
    # Save Index
    faiss.write_index(index, index_path)
    
    # Save Metadata
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
                "title": exp.title,
                "company": exp.company,
                "period": exp.period,
                "description": exp.description,
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
    try:
        index = faiss.read_index(index_path)
        with open(data_path, 'r', encoding='utf-8') as f:
            documents = json.load(f)
    except Exception as e:
        logger.error(f"Error loading index/data for {index_name}: {e}")
        return []

    # Generate Query Embedding
    query_embedding_list = get_embedding(query_text)
    query_embedding = np.array([query_embedding_list], dtype=np.float32)
    faiss.normalize_L2(query_embedding)

    # Check for dimension mismatch (e.g. old index vs new model)
    if index.d != query_embedding.shape[1]:
        logger.warning(
            f"Dimension mismatch detected! Index: {index.d}, Query: {query_embedding.shape[1]}. "
            f"Deleting stale index '{index_name}' to force rebuild on next request."
        )
        try:
            if os.path.exists(index_path):
                os.remove(index_path)
            if os.path.exists(data_path):
                os.remove(data_path)
        except OSError as e:
            logger.error(f"Failed to delete stale index files: {e}")
        
        return []

    # Search
    k = min(top_n, index.ntotal)
    if k == 0:
        return []
        
    distances, indices = index.search(query_embedding, k)

    # Format Results
    results = []
    for i, idx in enumerate(indices[0]):
        if idx != -1:
            doc = documents[idx].copy() # Copy to avoid mutating original
            doc['match_score'] = float(distances[0][i])
            # Reconstruct embedding not strictly needed for basic search, avoiding complexity
            results.append(doc)
            
    return results
