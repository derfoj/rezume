
import os
import sys
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ajout du dossier racine au sys.path
sys.path.append(os.getcwd())

from src.agents.generator import GeneratorAgent

def test_new_compilation_engine():
    print("🚀 Test du nouveau système de compilation multi-moteur...")
    
    agent = GeneratorAgent()
    
    # Profil minimal pour le test
    profile = {
        "name": "Test Moteur",
        "title": "Ingénieur Compilation",
        "summary": "Ceci est un test pour valider le basculement vers TexLive.net.",
        "email": "test@moteur.com",
        "experiences": [],
        "skills": ["LaTeX", "Python", "Robustesse"]
    }
    
    # Code LaTeX minimal et valide
    latex_code = r"""
\documentclass[11pt,a4paper]{article}
\begin{document}
\section*{Test de Robustesse}
Ce document a été généré pour tester le basculement vers l'API de secours.
\end{document}
"""
    
    output_dir = Path("outputs/tests")
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = output_dir / "test_engine.pdf"
    
    print("\n--- Tentative de compilation en ligne (TexLive.net) ---")
    success = agent.compile_latex_online(latex_code, pdf_path)
    
    if success and pdf_path.exists():
        print(f"✅ SUCCÈS : Le PDF a été généré via l'API. Taille : {pdf_path.stat().st_size} octets")
    else:
        print("❌ ÉCHEC : L'API n'a pas pu générer le PDF.")

if __name__ == "__main__":
    test_new_compilation_engine()
