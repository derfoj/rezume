# src/agents/parser.py
import json
import re
import logging
from src.core.utils import load_yaml
from src.core.llm_provider import get_llm

# Configure a logger for this module
logger = logging.getLogger(__name__)

class ParserAgent:
    def __init__(self, prompt_path: str):
        self.prompt_cfg = load_yaml(prompt_path)
        try:
            self.llm = get_llm()
            logger.info("ParserAgent initialized successfully with LLM.")
        except NotImplementedError:
            self.llm = None
            logger.warning("LLM provider not implemented, ParserAgent will use rule-based fallback.")

    def _rule_based_extract(self, text: str):
        """A simple fallback extraction method based on keywords."""
        logger.info("Executing rule-based extraction as a fallback.")
        text_lower = text.lower()
        techs = ["python", "sql", "pandas", "scikit-learn", "machine learning", "flask", "docker", "power bi", "tableau"]
        skills = [s for s in techs if s in text_lower]
        
        # Heuristic to detect verb phrases as missions
        missions = re.findall(r"(analyser|nettoyer|créer|développer|implémenter|déployer)[^\.]*", text_lower)
        return {"skills": skills, "missions": missions, "values": []}

    def extract_information(self, offer_text: str):
        """
        Extracts structured information from job offer text using an LLM.
        Falls back to a rule-based method if the LLM is unavailable or parsing fails.
        """
        if self.llm is None:
            return self._rule_based_extract(offer_text)

        template = self.prompt_cfg["template"]
        prompt = template.replace("{{offer_text}}", offer_text)
        
        try:
            resp = self.llm.chat(prompt)
        except Exception as e:
            logger.error(f"An error occurred during the LLM call: {e}", exc_info=True)
            return self._rule_based_extract(offer_text)

        # Attempt to parse the LLM response
        try:
            # First, try to parse the whole response directly
            return json.loads(resp)
        except json.JSONDecodeError:
            # If that fails, look for a JSON code block (e.g., ```json ... ```)
            logger.warning("Direct JSON parsing failed. Searching for a JSON code block.")
            match = re.search(r"```json\s*(\{.*?\})\s*```", resp, re.DOTALL)
            if not match:
                # If no code block, look for a raw JSON object
                match = re.search(r"(\{.*?\})", resp, re.DOTALL)

            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError as e:
                    logger.error(
                        f"Failed to parse the extracted JSON block: {e}\nBlock content: '{match.group(1)}'",
                        exc_info=True
                    )
            else:
                logger.warning("No parsable JSON block found in the LLM response.")
        
        # If all parsing attempts fail, fallback to rule-based method
        return self._rule_based_extract(offer_text)
