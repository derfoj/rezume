from typing import Dict, List

class OptimizerAgent:
    def __init__(self):
        pass

    def select_relevant_experiences(self, user_data: Dict, parsed_offer: Dict) -> List[Dict]:
        """
        Sélectionne et score les expériences selon la pertinence (MVP heuristic).
        - user_data: contenu JSON de knowledge_base.json (dict)
        - parsed_offer: output de ParserAgent.extract_information
        """
        offer_skills = [s.lower() for s in parsed_offer.get("skills", [])]
        offer_missions = [m.lower() for m in parsed_offer.get("missions", [])]

        selected = []
        for exp in user_data.get("experiences", []):
            score = 0
            desc = (exp.get("description") or "").lower()
            # compter correspondances skills
            for s in offer_skills:
                if s and s in desc:
                    score += 1
            # compter correspondances missions (verbes)
            for m in offer_missions:
                if m and m in desc:
                    score += 0.8
            if score > 0:
                exp_copy = dict(exp)  # éviter mutation sur kb originale
                exp_copy["relevance_score"] = round(score, 2)
                selected.append(exp_copy)

        selected.sort(key=lambda x: x["relevance_score"], reverse=True)
        # renvoyer top 3 (ou moins)
        return selected[:3]
