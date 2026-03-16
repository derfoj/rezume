import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from src.core.vector_store import build_vector_store, search_vector_store

def test_vector_store_search_logic():
    """Vérifie que la recherche renvoie les documents les plus proches (Mocking OpenAI)"""
    
    # 1. Préparer des documents fictifs
    docs = [
        {"content": "Expert en Python et FastAPI", "id": 1},
        {"content": "Expert en Java et Spring Boot", "id": 2},
        {"content": "Designer UI/UX", "id": 3}
    ]
    
    # 2. Simuler les embeddings OpenAI
    # Python -> [1, 0, 0], Java -> [0, 1, 0], Design -> [0, 0, 1]
    mock_embeddings = [
        [1.0] + [0.0]*1535,
        [0.0, 1.0] + [0.0]*1534,
        [0.0, 0.0, 1.0] + [0.0]*1533
    ]
    
    with patch('src.core.vector_store.get_embeddings', return_value=mock_embeddings):
        build_vector_store(docs, index_name="test_search")
    
    # 3. Simuler une requête "Python"
    # La requête est proche de [1, 0, 0]
    with patch('src.core.vector_store.get_embedding', return_value=[0.9, 0.1] + [0.0]*1534):
        results = search_vector_store("Développeur Python", index_name="test_search", top_n=1)
        
        assert len(results) > 0
        assert "Python" in results[0]["content"]
        assert results[0]["id"] == 1
