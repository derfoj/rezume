import faiss
import numpy as np
import os
import json
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from src.config.constants import EMBEDDINGS_DIR

# Use the same model as before for consistency
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
model = SentenceTransformer(MODEL_NAME)

def build_vector_store(experiences: List[Dict[str, Any]], index_name: str = "kb_index"):
    """
    Builds and saves a FAISS index and a corresponding JSON data file for experiences.
    """
    if not experiences:
        print("No experiences provided to build vector store.")
        return

    os.makedirs(EMBEDDINGS_DIR, exist_ok=True)
    
    # Prepare file paths
    index_path = os.path.join(EMBEDDINGS_DIR, f"{index_name}.faiss")
    data_path = os.path.join(EMBEDDINGS_DIR, f"{index_name}.json")

    # Create text representations for embedding
    experience_texts = [
        f"{exp.get('title', '')}: {exp.get('description', '')}" for exp in experiences
    ]

    # Generate embeddings
    print(f"Generating embeddings for {len(experience_texts)} experiences...")
    embeddings = model.encode(experience_texts, convert_to_tensor=False, show_progress_bar=True)
    embeddings = np.array(embeddings, dtype=np.float32)

    # Build FAISS index
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    
    # Save the index and the corresponding data
    print(f"Saving FAISS index to {index_path}")
    faiss.write_index(index, index_path)
    
    print(f"Saving experience data to {data_path}")
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(experiences, f, ensure_ascii=False, indent=4)

def search_vector_store(
    query_text: str, 
    index_name: str = "kb_index", 
    top_n: int = 3
) -> List[Dict[str, Any]]:
    """
    Searches a FAISS index to find the most relevant experiences for a query text.
    """
    index_path = os.path.join(EMBEDDINGS_DIR, f"{index_name}.faiss")
    data_path = os.path.join(EMBEDDINGS_DIR, f"{index_name}.json")

    if not os.path.exists(index_path) or not os.path.exists(data_path):
        # This case will be handled by the orchestrator, which will call build_vector_store
        return []

    # Load the index and data
    index = faiss.read_index(index_path)
    with open(data_path, 'r', encoding='utf-8') as f:
        experiences = json.load(f)

    # Embed the query
    query_embedding = model.encode([query_text])
    query_embedding = np.array(query_embedding, dtype=np.float32)

    # Search the index
    distances, indices = index.search(query_embedding, top_n)

    # Retrieve the matched experiences
    matched_experiences = [experiences[i] for i in indices[0]]
    
    # Optionally, add match scores (lower distance is better for L2)
    for i, exp in enumerate(matched_experiences):
        exp['match_score'] = float(1 - distances[0][i]) # Convert np.float32 to float

    return matched_experiences

