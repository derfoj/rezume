import logging
import os
from src.core.llm_provider import get_llm

logger = logging.getLogger(__name__)

class OptimizerAgent:
    def __init__(self):
        # We use the same LLM provider logic as elsewhere
        self.llm = self._get_llm_client()

    def _get_llm_client(self):
        # Quick factory to get the best available model for text generation
        from src.core.llm_provider import get_llm
        # Using the standard get_llm which handles provider selection from env/settings
        return get_llm()

    def optimize_description(self, text: str) -> str:
        """
        Rewrites a job description using the STAR method (Situation, Task, Action, Result).
        """
        if not text or len(text) < 10:
            return text

        prompt = f"""
        Tu es un expert en rédaction de CV et en coaching de carrière.
        Ta mission est de réécrire la description d'expérience professionnelle ci-dessous pour la rendre plus percutante.

        Méthode à utiliser : STAR (Situation, Tâche, Action, Résultat).
        
        Consignes :
        1. Utilise des verbes d'action forts à l'infinitif ou au passé composé (ex: "Développer", "Avoir géré").
        2. Sois concis et direct (style bullet points).
        3. Mets en avant les résultats quantifiables si le texte original le permet (chiffres, %, temps gagné).
        4. Ne pas inventer de faits, mais sublimer ceux existants.
        5. Le résultat doit être prêt à être copié-collé dans un CV (pas de texte d'intro "Voici la version corrigée...").

        Description originale :
        "{text}"

        Description optimisée (format bullet points si plusieurs idées, ou paragraphe dense) :
        """

        try:
            # The get_llm wrapper returns an object with a .chat() method
            response = self.llm.chat(prompt)
            return response.strip()
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            raise ValueError("Failed to optimize text with AI.")
