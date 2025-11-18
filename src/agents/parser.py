# src/agents/parser.py
import json
from src.core.utils import load_yaml
from src.core.llm_provider import get_llm

class ParserAgent:
    def __init__(self, prompt_path: str):
        self.prompt_cfg = load_yaml(prompt_path)
        try:
            self.llm = get_llm()
        except NotImplementedError:
            self.llm = None  # fallback to rule-based

    def _rule_based_extract(self, text: str):
        # Simple fallback extraction (keywords)
        textl = text.lower()
        techs = ["python", "sql", "pandas", "scikit-learn", "machine learning", "flask", "docker", "power bi", "tableau"]
        skills = [s for s in techs if s in textl]
        # missions: detect verbs phrases (heuristic)
        import re
        missions = re.findall(r"(analyser|nettoyer|créer|développer|implémenter|déployer)[^\.]*", textl)
        return {"skills": skills, "missions": missions, "values": []}

    def extract_information(self, offer_text: str):
        if self.llm is None:
            return self._rule_based_extract(offer_text)

        template = self.prompt_cfg["template"]
        prompt = template.replace("{{offer_text}}", offer_text)
        resp = self.llm.chat(prompt)
        # try parse JSON
        try:
            parsed = json.loads(resp)
            return parsed
        except Exception:
            # try to extract first {...} JSON block
            import re
            m = re.search(r"\{.*\}", resp, re.S)
            if m:
                try:
                    return json.loads(m.group(0))
                except:
                    pass
            # fallback
            return self._rule_based_extract(offer_text)
