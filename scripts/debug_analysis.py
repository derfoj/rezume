import logging
import os
from src.core.orchestration import parser_agent, _diversify_results
from src.core.vector_store import search_vector_store
from src.core.database import SessionLocal
from src.core.knowledge_base import get_profile_from_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_analysis():
    print("--- 1. Testing Parser ---")
    raw_text = "Nous cherchons un Développeur IA avec des compétences en Python, SQL et Machine Learning."
    try:
        parsed = parser_agent.extract_information(raw_text)
        print(f"Parsed Skills: {parsed.get('skills')}")
    except Exception as e:
        print(f"Parser Error: {e}")

    print("\n--- 2. Testing Vector Search ---")
    user_id = 1
    query_str = "Skills: Python, SQL, Machine Learning"
    index_name = f"user_{user_id}"
    
    results = search_vector_store(query_str, index_name=index_name, top_n=5)
    print(f"Raw Search Results: {len(results)}")
    for i, r in enumerate(results):
        has_emb = 'embedding' in r
        print(f"Result {i}: {r.get('metadata', {}).get('title')} | Embedding present: {has_emb}")
        if has_emb:
            print(f"  Embedding sample: {r['embedding'][:3]}...")

    print("\n--- 3. Testing Diversification ---")
    diversified = _diversify_results(results, top_n=3)
    print(f"Diversified Results: {len(diversified)}")

if __name__ == "__main__":
    test_analysis()
