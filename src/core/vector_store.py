import faiss
import numpy as np
import os
import json
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from src.config.constants import EMBEDDINGS_DIR
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Use a consistent model for generating embeddings
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
model = SentenceTransformer(MODEL_NAME)

def build_vector_store(experiences: List[Dict[str, Any]], index_name: str = "kb_index"):
    """
    Builds and saves a FAISS index using cosine similarity (Inner Product)
    and a corresponding JSON data file for experiences, with embeddings included.
    """
    if not experiences:
        logger.warning("No experiences provided to build vector store.")
        return

    os.makedirs(EMBEDDINGS_DIR, exist_ok=True)
    
    index_path = os.path.join(EMBEDDINGS_DIR, f"{index_name}.faiss")
    data_path = os.path.join(EMBEDDINGS_DIR, f"{index_name}.json")

    experience_texts = [f"{exp.get('title', '')}: {exp.get('description', '')}" for exp in experiences]

    logger.info(f"Generating embeddings for {len(experience_texts)} experiences...")
    embeddings = model.encode(experience_texts, convert_to_tensor=False, show_progress_bar=True)
    embeddings = np.array(embeddings, dtype=np.float32)
    
    # Store the embedding with the experience data
    for i, exp in enumerate(experiences):
        exp['embedding'] = embeddings[i].tolist() # Store as list for JSON serialization

    faiss.normalize_L2(embeddings)

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    
    logger.info(f"Saving FAISS index to {index_path}")
    faiss.write_index(index, index_path)
    
    logger.info(f"Saving experience data with embeddings to {data_path}")
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(experiences, f, ensure_ascii=False, indent=4)

def search_vector_store(
    query_text: str, 
    index_name: str = "kb_index", 
    top_n: int = 3
) -> List[Dict[str, Any]]:
    """
    Searches a FAISS index using cosine similarity to find the most relevant experiences.
    """
    index_path = os.path.join(EMBEDDINGS_DIR, f"{index_name}.faiss")
    data_path = os.path.join(EMBEDDINGS_DIR, f"{index_name}.json")

    if not os.path.exists(index_path) or not os.path.exists(data_path):
        logger.warning(f"Index '{index_name}' not found. Returning empty results.")
        return []

    # Load the index and data
    index = faiss.read_index(index_path)
    with open(data_path, 'r', encoding='utf-8') as f:
        experiences = json.load(f)

    # Embed and normalize the query
    query_embedding = model.encode([query_text])
    query_embedding = np.array(query_embedding, dtype=np.float32)
    faiss.normalize_L2(query_embedding) # Normalize query vector

    # Search the index; for IP, higher values are better
    distances, indices = index.search(query_embedding, top_n)

    # Retrieve the matched experiences
    matched_experiences = []
    for i, idx in enumerate(indices[0]):
        if idx != -1:  # FAISS uses -1 for no result
            exp = experiences[idx]
            # The distance for IP is the cosine similarity score
            exp['match_score'] = float(distances[0][i])
            matched_experiences.append(exp)
            
    return matched_experiences
