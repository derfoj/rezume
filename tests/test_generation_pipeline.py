import pytest
import os
from unittest.mock import MagicMock, patch
from pathlib import Path
from src.agents.generator import GeneratorAgent

# --- 1. Test de l'Initialisation de l'Agent ---
def test_generator_agent_init():
    """Vérifie que l'agent peut s'initialiser sans crash"""
    with patch('src.agents.generator.get_llm') as mock_get_llm:
        agent = GeneratorAgent(provider="openai", model="gpt-4o-mini")
        assert agent is not None
        mock_get_llm.assert_called_once()

# --- 2. Test du Nettoyage de l'Output LLM ---
def test_clean_llm_output():
    """Vérifie que l'agent extrait correctement le LaTeX des blocs Markdown"""
    agent = GeneratorAgent()
    dirty_output = "Voici le code :\n```latex\n\\documentclass{article}\n\\begin{document}\nTest\n\\end{document}\n```\nJ'espère que ça aide."
    clean_code = agent._clean_llm_output(dirty_output)
    assert clean_code.startswith("\\documentclass")
    assert clean_code.endswith("\\end{document}")
    assert "J'espère que ça aide" not in clean_code

# --- 3. Test de la Génération de Source LaTeX ---
def test_generate_latex_source():
    """Vérifie que l'agent génère le code source LaTeX attendu et sauvegarde le fichier"""
    with patch('src.agents.generator.get_llm') as mock_get_llm:
        mock_llm = MagicMock()
        mock_llm.chat.return_value = "\\documentclass{article}\\begin{document}Test CV\\end{document}"
        mock_get_llm.return_value = mock_llm
        
        agent = GeneratorAgent()
        user_profile = {"name": "John Doe", "photo_path": "some_path.png"}
        experiences = [{"title": "Dev"}]
        
        source = agent.generate_latex_source(user_profile, experiences, session_id="test_session")
        
        assert "\\documentclass" in source
        assert "Test CV" in source
        # Vérifie la normalisation du chemin de la photo pour SwiftLaTeX
        assert user_profile["photo_path"] == "photo_cv.png"
        
        # Vérifie que le fichier a été créé
        tex_path = Path("outputs/generated_cvs/test_session/cv_test_session.tex")
        assert tex_path.exists()
        
        # Cleanup
        import shutil
        shutil.rmtree(tex_path.parent)

# --- 4. Test de Gestion d'Erreur LLM ---
def test_generation_error_handling():
    """Vérifie que l'agent lève une RuntimeError si le LLM échoue"""
    with patch('src.agents.generator.get_llm') as mock_get_llm:
        mock_llm = MagicMock()
        mock_llm.chat.side_effect = Exception("LLM Down")
        mock_get_llm.return_value = mock_llm
        
        agent = GeneratorAgent()
        with pytest.raises(RuntimeError, match="L'IA a échoué"):
            agent.generate_latex_source({"name": "Test"}, [])
