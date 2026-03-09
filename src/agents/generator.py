# src/agents/generator.py
import os
import json
import subprocess
import uuid
import gc
from pathlib import Path
from typing import List, Dict, Any

from src.core.utils import load_yaml, load_text
from src.core.llm_provider import get_llm
from src.config.constants import TEMPLATES_DIR

def clean_unicode_for_latex(text: str) -> str:
    """Remplace les caractères Unicode qui font planter pdflatex."""
    replacements = {
        "ᵉ": r"\textsuperscript{e}", "’": "'", "…": "...", "–": "--", "—": "---",
        "€": r"\euro{}", "«": r"\guillemotleft{}", "»": r"\guillemotright{}"
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text

def escape_latex_special_chars(text: str) -> str:
    """Échappe les caractères spéciaux LaTeX."""
    if not isinstance(text, str): return text
    chars = {
        "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
        "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
    }
    for char, escaped in chars.items():
        text = text.replace(char, escaped)
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
            raise RuntimeError("IA non disponible pour la génération.")

        # Nettoyage des données
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

        # Appel LLM
        raw_output = self.llm.chat(prompt)
        clean_latex = self._clean_llm_output(clean_unicode_for_latex(raw_output))

        # Dossier de session
        if not session_dir:
            base_name = f"rezume_llm_{uuid.uuid4()}"
            session_dir = Path(__file__).resolve().parent.parent.parent / "outputs/generated_cvs" / base_name
            os.makedirs(session_dir, exist_ok=True)
        else:
            base_name = session_dir.name
        
        session_dir = Path(session_dir)
        tex_path, pdf_path = session_dir / f"{base_name}.tex", session_dir / f"{base_name}.pdf"
        tex_path.write_text(clean_latex, encoding="utf-8")

        # Compilation
        success = False
        try:
            # Test local (si pdflatex est là)
            subprocess.run(["pdflatex", "-interaction=nonstopmode", f"-output-directory={session_dir}", str(tex_path)], capture_output=True, timeout=20)
            if pdf_path.exists(): success = True
        except: pass

        if not success:
            # Fallback API ultra-robuste
            try:
                import requests
                # On envoie le code brut dans le body pour éviter les limites de taille d'URL
                res = requests.post("https://latexonline.cc/compile", data={"text": clean_latex}, timeout=45)
                if res.status_code == 200:
                    pdf_path.write_bytes(res.content)
                    success = True
            except Exception as e:
                print(f"Erreur API LatexOnline: {e}")

        if not success:
            raise RuntimeError("Impossible de générer le PDF. Vérifiez votre syntaxe LaTeX.")
        
        gc.collect() # Libère la RAM immédiatement
        return str(pdf_path), str(tex_path)
