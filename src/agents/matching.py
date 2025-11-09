from typing import List, Dict

def select_experience(knowledge_base: Dict, offer_data: Dict) -> List[Dict]:
    """
    Sélectionne les expériences les plus pertinentes
    en fonction des compétences présentes dans l'offre.
    """
    selected = []
    offer_skills = [s.lower() for s in offer_data.get("skills", [])]

    for exp in knowledge_base.get("experiences", []):
        match_score = 0
        for skill in offer_skills:
            if skill in exp["description"].lower():
                match_score += 1
        if match_score > 0:
            exp["match_score"] = match_score
            selected.append(exp)

    selected.sort(key=lambda x: x["match_score"], reverse=True)
    return selected[:3]
