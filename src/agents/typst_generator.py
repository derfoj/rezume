import os
import json
import uuid
import logging
import typst
from pathlib import Path
from typing import List, Dict, Any

from src.core.utils import load_yaml, load_text
from src.core.llm_provider import get_llm
from src.config.constants import TEMPLATES_DIR

logger = logging.getLogger(__name__)

class TypstGeneratorAgent:
    """
    Agent responsable de la génération du CV via Typst.
    Utilise l'IA pour structurer le contenu et la bibliothèque 'typst' pour le rendu PDF.
    """
    def __init__(self, provider: str = None, model: str = None, api_key: str = None):
        try:
            self.llm = get_llm(provider=provider, model=model, user_api_key=api_key)
            logger.info(f"✅ TypstGeneratorAgent prêt ({provider or 'default'}/{model or 'default'}).")
        except Exception as e:
            self.llm = None
            logger.error(f"❌ Erreur lors de l'init du TypstGeneratorAgent: {e}")

    def _clean_llm_output(self, typst_code: str) -> str:
        """
        Extrait proprement le code Typst de la réponse de l'LLM.
        """
        import re
        # Chercher les blocs de code Markdown
        match = re.search(r"```(?:typst|typ|rust)?\s*(.*?)\s*```", typst_code, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Si pas de bloc, on nettoie juste le texte (souvent le cas si l'LLM suit bien les instructions)
        return typst_code.strip()

    def generate_cv(self, user_profile: Dict[str, Any], experiences: List[Dict[str, Any]], template_name: str = "modern", feedback: str = None, session_id: str = None) -> (str, str): 
        """
        Génère un CV au format PDF via Typst.
        Retourne (pdf_path, typ_path).
        """
        if not self.llm:
            raise RuntimeError("TypstGeneratorAgent non initialisé.")

        # Chargement du template Typst (on réutilise le nom mais en .typ)
        template_path = TEMPLATES_DIR / f"{template_name}.typ"
        if not template_path.exists():
            template_path = TEMPLATES_DIR / "modern.typ"
        
        template_content = load_text(template_path)
        prompt_config = load_yaml("src/config/prompts/typst_generator.yaml")
        prompt_template = prompt_config['template']

        # Préparation du prompt
        num_experiences = len(experiences)
        verbosity_instruction = "HAUTE VERBOSITÉ : étoffe chaque point." if num_experiences <= 3 else "CONCIS : optimise pour 1 page."

        final_prompt = prompt_template.replace(
            "{{user_profile}}", json.dumps(user_profile, indent=2, ensure_ascii=False)
        ).replace(
            "{{selected_experiences}}", json.dumps(experiences, indent=2, ensure_ascii=False)
        ).replace(
            "{{cv_template}}", template_content
        ).replace(
            "{{verbosity_instruction}}", verbosity_instruction
        )

        if feedback:
            final_prompt = f"NOTE PRÉCÉDENTE : {feedback}\n\n" + final_prompt

        try:
            # Appel à l'IA
            generated_args = self.llm.chat(final_prompt)
            generated_args = self._clean_llm_output(generated_args)
            
            # On s'assure que c'est bien entouré de parenthèses si l'IA les a oubliées
            if not generated_args.strip().startswith("("):
                generated_args = f"({generated_args})"
                
        except Exception as e:
            raise RuntimeError(f"L'IA a échoué à générer les arguments Typst : {e}")

        # Gestion des fichiers
        unique_id = session_id or str(uuid.uuid4())
        session_dir = Path("outputs/generated_cvs") / unique_id
        session_dir.mkdir(parents=True, exist_ok=True)

        typ_path = session_dir / f"cv_{unique_id}.typ"
        pdf_path = session_dir / f"cv_{unique_id}.pdf"

        # On combine le template et l'appel généré par l'IA
        full_code = template_content + "\n\n#resume" + generated_args

        with open(typ_path, "w", encoding="utf-8") as f:
            f.write(full_code)

        # --- RENDU TYPST ---
        logger.info(f"🚀 Rendu PDF avec Typst (Session: {unique_id})...")
        try:
            # On utilise le fichier physique pour éviter les erreurs de chemin sur Windows
            pdf_bytes = typst.compile(str(typ_path))
            with open(pdf_path, "wb") as f:
                f.write(pdf_bytes)
            logger.info("✅ PDF généré avec succès via Typst.")
        except Exception as e:
            logger.error(f"❌ Erreur de compilation Typst : {e}")
            raise RuntimeError(f"La compilation Typst a échoué : {e}")

        return str(pdf_path), str(typ_path)
