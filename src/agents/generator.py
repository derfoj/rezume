import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Dict, List

class GeneratorAgent:
    def __init__(self):
        pass

    def generate_cv(self,
                    user_data: Dict,
                    selected_experiences: List[Dict],
                    template_path: str,
                    output_path: str) -> str:
        """
        Rend le template Jinja2 avec user_data + selected_experiences.
        - template_path peut être "data/cv_template.txt" (ou src/interfaces/...)
        - output_path : fichier texte en sortie
        """
        # déterminer dossier template
        template_dir, template_name = os.path.split(template_path)
        if template_dir == "":
            template_dir = "."

        env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape()
        )
        template = env.get_template(template_name)

        # préparer context
        context = {
            "name": user_data.get("name"),
            "title": user_data.get("title"),
            "summary": user_data.get("summary"),
            "skills": user_data.get("skills", []),
            "soft_skills": user_data.get("soft_skills", []),
            "experiences": selected_experiences,
            "education": user_data.get("education", [])
        }

        rendered = template.render(**context)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered)

        return output_path
