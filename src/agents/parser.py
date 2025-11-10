# src/agents/parser.py
import re
from typing import Dict, List

class ParserAgent:
    def __init__(self):
        # mots-clés techniques simples pour MVP — tu les enrichiras ensuite
        self.tech_keywords = [
            "python", "sql", "pandas", "scikit-learn", "machine learning",
            "flask", "docker", "power bi", "tableau", "api", "tensorflow"
        ]

    def extract_information(self, offer_text: str) -> Dict:
        """
        Nettoie et extrait des informations clés d'une offre.
        Retourne dict: {'skills': [...], 'missions':[...], 'raw_text': str}
        """
        text = (offer_text or "").strip()
        cleaned = re.sub(r"[\r\n\t]+", " ", text)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        lower = cleaned.lower()

        skills = [kw for kw in self.tech_keywords if kw in lower]

        # chercher phrases contenant verbes d'action usuels
        keywords = [
            "analyser", "développer", "implémenter", "construire",
            "créer","déployer","optimiser", "nettoyer", "contribuer","traitement"

        ]
        pattern = r"(" + "|".join(keywords) + r")[^\.]+"
        missions = re.findall(pattern, lower)
        # garder les missions uniques et limitées
        missions = list(dict.fromkeys([m.strip() for m in missions]))[:8]

        return {
            "skills": skills,
            "missions": missions,
            "raw_text": cleaned
        }
