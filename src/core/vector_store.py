import faiss
import numpy as np
import os
from openai import OpenAI
from src.config.constants import EMBEDDINGS_DIR, MODEL_NAME

client = OpenAI()

def embed_texts(texts: list[str]) -> np.ndarray:
    response = client.embeddings.create(
        input=texts,
        model=MODEL_NAME
    )
    return np.array([d.embedding for d in response.data], dtype=np.float32)

def build_vector_store(texts: list[str], file_name="kb_index.faiss"):
    os.makedirs(EMBEDDINGS_DIR, exist_ok=True)
    embeddings = embed_texts(texts)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings) #ignore l'erreur là !
    faiss.write_index(index, f"{EMBEDDINGS_DIR}/{file_name}")
