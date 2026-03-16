import os
import requests
from pathlib import Path
from src.agents.generator import GeneratorAgent

def test_live_latex_online():
    """
    Test RÉEL de l'API LatexOnline.
    Vérifie que le service est disponible et compile un document simple.
    """
    agent = GeneratorAgent()
    # Petit code LaTeX minimal pour le test
    latex_code = r"""
\documentclass{article}
\begin{document}
Test de compilation Live pour reZume.
\end{document}
"""
    output_path = Path("live_test.pdf")
    
    print("\n--- Test Live LatexOnline ---")
    success = agent.compile_latex_online(latex_code, output_path)
    
    if success:
        print("✅ Succès : Le PDF a été généré via l'API.")
        assert output_path.exists()
        assert output_path.stat().st_size > 0
        os.remove(output_path)
    else:
        print("❌ Échec : L'API LatexOnline n'a pas répondu ou a renvoyé une erreur.")
        pytest.fail("L'API de secours (LatexOnline) est indisponible.")

if __name__ == "__main__":
    # Permet de lancer le test directement avec python tests/test_live_generation.py
    import pytest
    pytest.main([__file__])
