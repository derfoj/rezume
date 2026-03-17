
import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(os.getcwd())

from src.agents.generator import GeneratorAgent
from src.core.llm_provider import get_llm

def test_unicode_generation():
    print("Testing CV generation with Unicode characters...")
    
    agent = GeneratorAgent()
    if not agent.llm:
        print("❌ LLM not initialized. Check your .env file.")
        return

    profile = {
        "name": "Élodie L’héritier ᵉ",
        "title": "Ingénieure Spécialiste ✨",
        "summary": "Expérience en € et … avec des symboles comme ¹ ² ³.",
        "email": "test@example.com",
        "portfolio_url": "https://example.com",
        "linkedin_url": "https://linkedin.com/in/test",
        "photo_path": "man_laptop",
        "skills": ["Python 3.x", "R² Analysis", "LaTeX Expert"],
        "soft_skills": ["Leadership 🚀", "Communication"],
        "education": [],
        "languages": []
    }
    
    experiences = [
        {
            "title": "Data Scientist Senior ᵉ",
            "company": "Tech & Co",
            "date": "2020 - Présent",
            "description": "Utilisation de modèles d'IA pour optimiser les profits de 15% (±2%)."
        }
    ]
    
    try:
        pdf_path, tex_path = agent.generate_cv_from_llm(profile, experiences, template_name="modern")
        print(f"✅ Success! PDF: {pdf_path}")
        print(f"✅ TeX source: {tex_path}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_unicode_generation()
