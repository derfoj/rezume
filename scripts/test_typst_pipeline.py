import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ajout du root au path pour les imports
sys.path.append(str(Path(__file__).parent.parent))

# Chargement du .env
load_dotenv()

from src.agents.typst_generator import TypstGeneratorAgent

def test_full_typst_pipeline():
    print("--- Test du Pipeline Complet Typst ---")
    
    # Initialisation de l'agent
    agent = TypstGeneratorAgent()
    
    # Données de test
    user_profile = {
        "name": "Alexandre Dumas",
        "title": "Architecte Solutions Cloud",
        "email": "alexandre.dumas@cloud.com",
        "phone": "06 00 00 00 00",
        "linkedin_url": "linkedin.com/in/alexcloud",
        "portfolio_url": "alexcloud.io",
        "summary": "Expert en architectures distribuées et Kubernetes avec plus de 10 ans d'expérience.",
        "hard_skills": "AWS, GCP, Terraform, Kubernetes, Python, Go",
        "soft_skills": "Leadership, Communication, Résolution de problèmes",
        "languages": "Français (Natif), Anglais (Bilingue), Espagnol (Intermédiaire)"
    }
    
    experiences = [
        {
            "company": "CloudNine Systems",
            "date": "2020 - Présent",
            "position": "Principal Architect",
            "description": "Migration de 500+ microservices vers Kubernetes. Réduction des coûts d'infrastructure de 40%."
        },
        {
            "company": "DataFlow Corp",
            "date": "2015 - 2020",
            "position": "Senior Developer",
            "description": "Conception d'un moteur de traitement de données temps réel gérant 1To/jour."
        }
    ]
    
    try:
        pdf_path, typ_path = agent.generate_cv(
            user_profile=user_profile,
            experiences=experiences,
            template_name="modern",
            session_id="test_session_typst"
        )
        
        print(f"✅ Pipeline réussi !")
        print(f"📄 PDF : {pdf_path}")
        print(f"📝 Typst : {typ_path}")
        
    except Exception as e:
        print(f"❌ Échec du pipeline : {e}")

if __name__ == "__main__":
    test_full_typst_pipeline()
