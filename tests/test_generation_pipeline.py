import pytest
import os
from unittest.mock import MagicMock, patch
from pathlib import Path
from src.agents.generator import GeneratorAgent
from src.core.knowledge_base import Profile, Experience

# --- 1. Test de l'Initialisation de l'Agent ---
def test_generator_agent_init():
    """Vérifie que l'agent peut s'initialiser sans crash (même sans clé API pour le test)"""
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

# --- 3. Test de la Compilation Cloud (LatexOnline) ---
@pytest.mark.asyncio
async def test_compile_latex_online_success():
    """Vérifie que l'appel à l'API LatexOnline fonctionne (mocké)"""
    agent = GeneratorAgent()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"PDF_CONTENT"
    
    with patch('requests.post', return_value=mock_response):
        output_path = Path("test_output.pdf")
        success = agent.compile_latex_online("\\documentclass{article}\\begin{document}Test\\end{document}", output_path)
        assert success is True
        assert output_path.exists()
        # Cleanup
        if output_path.exists(): os.remove(output_path)

# --- 4. Test de la Logique de Résolution des Photos ---
def test_photo_path_resolution():
    """Vérifie que l'agent résout correctement les chemins des avatars"""
    agent = GeneratorAgent()
    user_profile = {"photo_path": "man_laptop"}
    experiences = []
    
    # Mock des dépendances pour ne pas appeler l'IA
    agent.llm = MagicMock()
    agent.llm.chat.return_value = "\\documentclass{article}\\begin{document}Test\\end{document}"
    
    with patch('pathlib.Path.exists', return_value=True):
        # On force le retour de generate_cv_from_llm pour éviter la compilation réelle
        with patch.object(agent, 'compile_latex_online', return_value=True):
            with patch('src.agents.generator.subprocess.run'):
                pdf, tex = agent.generate_cv_from_llm(user_profile, experiences)
                # Vérifie que l'ID man_laptop a été transformé en chemin vers avatar_man_laptop.png
                assert "avatar_man_laptop.png" in user_profile["photo_path"]

# --- 5. Test des Échecs de Compilation ---
def test_compilation_failure_handling():
    """Vérifie que l'agent lève une erreur si toutes les méthodes de compilation échouent"""
    agent = GeneratorAgent()
    agent.llm = MagicMock()
    agent.llm.chat.return_value = "invalid latex"
    
    with patch('src.agents.generator.subprocess.run', side_effect=FileNotFoundError):
        with patch.object(agent, 'compile_latex_online', return_value=False):
            with pytest.raises(RuntimeError, match="La compilation LaTeX a échoué"):
                agent.generate_cv_from_llm({"name": "Test"}, [])
