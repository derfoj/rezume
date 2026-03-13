# src/agents/generator.py
import os
import json
import subprocess
import uuid
import gc
import logging
from pathlib import Path
from typing import List, Dict, Any

from src.core.utils import load_yaml, load_text
from src.core.llm_provider import get_llm
from src.config.constants import TEMPLATES_DIR

logger = logging.getLogger(__name__)

def clean_unicode_for_latex(text: str) -> str:
    replacements = {
        "ᵉ": r"\textsuperscript{e}", "ʳ": "r", "’": "'", "…": "...", "–": "--", "—": "---",
        "€": r"\euro{}", "«": r"\guillemotleft{}", "»": r"\guillemotright{}"
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text

def escape_latex_special_chars(text: str) -> str:
    if not isinstance(text, str): return text
    
    # We first replace backslashes with a unique, temporary string
    # to avoid escaping the backslashes we are about to add.
    text = text.replace("\\", "TEMPORARYBACKSLASHHOLDER")
    
    chars = {
        "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
        "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
    }
    for char, escaped in chars.items():
        text = text.replace(char, escaped)
        
    text = text.replace("TEMPORARYBACKSLASHHOLDER", r"\textbackslash{}")
    return text

def sanitize_data_recursive(data):
    if isinstance(data, dict):
        return {k: sanitize_data_recursive(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_data_recursive(i) for i in data]
    elif isinstance(data, str):
        return escape_latex_special_chars(data)
    return data

class GeneratorAgent:
    def __init__(self, provider: str = None, model: str = None, api_key: str = None):
        try:
            self.llm = get_llm(provider=provider, model=model, user_api_key=api_key)
        except:
            self.llm = None

    def _clean_llm_output(self, latex_code: str) -> str:
        import re
        match = re.search(r"```(?:latex)?\s*(.*?)\s*```", latex_code, re.DOTALL | re.IGNORECASE)
        if match:
            code = match.group(1).strip()
            if code.startswith("\\documentclass"): return code
        
        start = latex_code.find("\\documentclass")
        if start != -1:
            latex_code = latex_code[start:]
        
        end = latex_code.find("\\end{document}")
        if end != -1:
            latex_code = latex_code[:end + 14]
            
        return latex_code.strip()

    def generate_cv_from_llm(self, user_profile: Dict[str, Any], experiences: List[Dict[str, Any]], template_name: str = "modern", feedback: str = None, session_dir: Path = None) -> (str, str):
        if not self.llm:
            raise RuntimeError("IA non disponible.")

        # --- GESTION ROBUSTE DE LA PHOTO ---
        photo_path = ""
        if user_profile.get("photo_path"):
            p = user_profile["photo_path"]
            # Si c'est un ID d'avatar, on cherche dans les assets
            avatar_map = {
                "man_laptop": "avatar_man_laptop.png", 
                "woman_laptop": "avatar_woman_laptop.png",
                "man_coffee": "avatar_man_coffee.png",
                "woman_rocket": "avatar_woman_rocket.png"
            }
            photo_name = avatar_map.get(p, p)
            
            # Chemins possibles (Vercel/Render friendly)
            root = Path(__file__).resolve().parent.parent.parent
            candidates = [
                root / "frontend/src/assets" / photo_name,
                root / "data/img" / photo_name,
                root / "data/img/uploads" / photo_name.split('/')[-1] # Cas des uploads
            ]
            
            for cand in candidates:
                if cand.exists():
                    photo_path = str(cand).replace("\\", "/")
                    break
        
        user_profile["photo_path"] = photo_path
        # -----------------------------------

        safe_profile = sanitize_data_recursive(user_profile)
        safe_experiences = sanitize_data_recursive(experiences)

        template_path = TEMPLATES_DIR / f"{template_name}.tex"
        if not template_path.exists(): template_path = TEMPLATES_DIR / "modern.tex"
        cv_template = load_text(template_path)
        
        prompt_config = load_yaml("src/config/prompts/generator.yaml")
        prompt = prompt_config['template'].replace("{{user_profile}}", json.dumps(safe_profile, ensure_ascii=False))\
                                          .replace("{{selected_experiences}}", json.dumps(safe_experiences, ensure_ascii=False))\
                                          .replace("{{cv_template}}", cv_template)\
                                          .replace("{{verbosity_instruction}}", "Fais tenir sur une page.")

        if feedback: prompt += f"\n\nCorrection : {feedback}"

        try:
            raw_output = self.llm.chat(prompt)
            clean_latex = self._clean_llm_output(clean_unicode_for_latex(raw_output))
        except Exception as e:
            logger.error(f"LLM Chat Error: {e}")
            raise RuntimeError("L'IA n'a pas pu générer le code LaTeX.")

        # Dossier de session
        unique_id = uuid.uuid4()
        base_name = f"rezume_llm_{unique_id}"
        if not session_dir:
            session_dir = Path(__file__).resolve().parent.parent.parent / "outputs/generated_cvs" / base_name
        
        session_dir = Path(session_dir)
        os.makedirs(session_dir, exist_ok=True)
        
        tex_path = session_dir / f"{base_name}.tex"
        pdf_path = session_dir / f"{base_name}.pdf"
        tex_path.write_text(clean_latex, encoding="utf-8")

        # Compilation
        success = False
        # 1. Tentative locale (uniquement si pdflatex est présent)
        try:
            res = subprocess.run(["pdflatex", "-version"], capture_output=True)
            if res.returncode == 0:
                subprocess.run(["pdflatex", "-interaction=nonstopmode", f"-output-directory={session_dir}", str(tex_path)], capture_output=True, timeout=30)
                if pdf_path.exists(): success = True
        except:
            pass

        # 2. Fallback API Externe (Si local échoue ou absent)
        api_error_message = None
        if not success:
            try:
                import requests
                # On utilise un timeout plus long pour les gros fichiers
                res = requests.post("https://latexonline.cc/compile", data={"text": clean_latex}, timeout=60)
                if res.status_code == 200:
                    pdf_path.write_bytes(res.content)
                    success = True
                else:
                    api_error_message = f"LatexOnline API Error: Status {res.status_code}. Content: {res.text[:200]}"
                    logger.error(api_error_message)
            except Exception as e:
                api_error_message = f"LatexOnline API Exception: {e}"
                logger.error(api_error_message)

        if not success:
            error_details = api_error_message if api_error_message else "Erreur locale Inconnue"
            logger.error(f"Echec final de la compilation. Détails: {error_details}")
            raise RuntimeError(f"La compilation du PDF a échoué. L'API LaTeX a retourné une erreur ou pdflatex est manquant. Détails: {error_details}")
        
        gc.collect()
        return str(pdf_path), str(tex_path)
