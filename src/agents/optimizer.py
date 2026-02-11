import logging
import os
from src.core.llm_provider import get_llm
from src.core.utils import load_yaml

logger = logging.getLogger(__name__)

class OptimizerAgent:
    def __init__(self):
        # We use the same LLM provider logic as elsewhere
        self.llm = self._get_llm_client()
        self.prompt_config = load_yaml("src/config/prompts/optimizer.yaml")

    def _get_llm_client(self):
        # Quick factory to get the best available model for text generation
        from src.core.llm_provider import get_llm
        # Using the standard get_llm which handles provider selection from env/settings
        return get_llm()

    def optimize_description(self, text: str, tone: str = "standard", job_offer: str = None) -> str:
        """
        Rewrites a job description using the STAR method with a specific tone, 
        potentially optimized for a specific job offer.
        Tones: standard, dynamic, formal, explanatory
        """
        if not text or len(text) < 10:
            return text

        tone_instructions = {
            "standard": "Adopte un ton professionnel équilibré. Utilise la méthode STAR.",
            "dynamic": "Adopte un ton énergique et punchy. Utilise des verbes d'action forts. Idéal pour startups/tech.",
            "formal": "Adopte un ton soutenu et académique. Vocabulaire précis et corporatif. Idéal pour banque/droit.",
            "explanatory": "Adopte un ton pédagogique et clair. Explique bien les concepts. Idéal pour junior/reconversion."
        }
        
        instruction = tone_instructions.get(tone, tone_instructions["standard"])
        
        context_prompt = ""
        if job_offer:
            context_prompt = f"\nOptimise la description en mettant en avant les compétences et missions pertinentes pour cette offre d'emploi :\n\"\"\"{job_offer}\"\"\"\n"

        prompt_template = self.prompt_config.get('template', '')
        prompt = prompt_template.replace("{{context_prompt}}", context_prompt)\
                                .replace("{{instruction}}", instruction)\
                                .replace("{{text}}", text)

        try:
            # The get_llm wrapper returns an object with a .chat() method
            response = self.llm.chat(prompt)
            return response.strip()
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            raise ValueError("Failed to optimize text with AI.")
