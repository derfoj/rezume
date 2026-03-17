# src/agents/generator.py
import os
import json
import subprocess
import uuid
import logging
import requests
from pathlib import Path
from typing import List, Dict, Any

from src.core.utils import load_yaml, load_text
from src.core.llm_provider import get_llm
from src.config.constants import TEMPLATES_DIR

logger = logging.getLogger(__name__)

def clean_unicode_for_latex(text: str) -> str:
    """
    Replaces common Unicode characters that break pdflatex with LaTeX equivalents.
    """
    replacements = {
        "ᵉ": r"\textsuperscript{e}",
        "¹": r"\textsuperscript{1}",
        "²": r"\textsuperscript{2}",
        "³": r"\textsuperscript{3}",
        "’": "'",
        "…": "...",
        "–": "--",
        "—": "---",
        "“": "``",
        "”": "''",
        "«": "\\guillemotleft{}",
        "»": "\\guillemotright{}",
        "€": "\\euro{}",
        "oe": "\\oe{}",
        "OE": "\\OE{}",
        "æ": "\\ae{}",
        "Æ": "\\AE{}"
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text

def escape_latex_special_chars(text: str) -> str:
    """
    Escapes LaTeX special characters in a string to prevent injection or compilation errors.
    """
    if not isinstance(text, str):
        return text

    chars = {
        "\\": r"\textbackslash{}", # Must be first to avoid escaping escapes
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }

    # Simple replacement loop
    for char, escaped in chars.items():
        text = text.replace(char, escaped)
    return text

def sanitize_data_recursive(data, skip_keys=None):
    """Recursively sanitizes dictionary or list values."""
    if skip_keys is None:
        skip_keys = set()

    if isinstance(data, dict):
        return {
            k: (v if k in skip_keys else sanitize_data_recursive(v, skip_keys))
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [sanitize_data_recursive(i, skip_keys) for i in data]
    elif isinstance(data, str):
        return escape_latex_special_chars(data)
    else:
        return data

class GeneratorAgent:
    """
    An agent responsible for generating the final LaTeX CV by calling an LLM
    with a complete context, then compiling the result to PDF.
    """
    def __init__(self, provider: str = None, model: str = None, api_key: str = None):
        try:
            self.llm = get_llm(provider=provider, model=model, user_api_key=api_key)
            logger.info(f"✅ GeneratorAgent prêt ({provider or 'default'}/{model or 'default'}).")
        except Exception as e:
            self.llm = None
            logger.error(f"❌ Erreur lors de l'init du GeneratorAgent: {e}")

    def _clean_llm_output(self, latex_code: str) -> str:
        """
        Robustly extracts LaTeX code from LLM output.
        """
        import re
        match = re.search(r"```(?:latex)?\s*(.*?)\s*```", latex_code, re.DOTALL | re.IGNORECASE)
        if match:
            clean_code = match.group(1).strip()
            if clean_code.startswith("\\documentclass"):
                return clean_code

        start_idx = latex_code.find("\\documentclass")
        if start_idx != -1:
            latex_code = latex_code[start_idx:]

        end_marker = "\\end{document}"
        end_idx = latex_code.find(end_marker)
        if end_idx != -1:
            latex_code = latex_code[:end_idx + len(end_marker)]

        return latex_code.strip()

    def compile_latex_online(self, latex_code: str, output_path: Path) -> bool:
        """
        Fallback compilation using TexLive.net API (more stable than LatexOnline).
        """
        api_url = "https://texlive.net/cgi-bin/latexcgi"
        logger.info(f"🌐 Tentative de compilation via {api_url} (Fallback)...")
        try:
            # TexLive.net expects 'filecontents[]' and 'filename[]'
            payload = {
                'filecontents[]': latex_code,
                'filename[]': 'main.tex',
                'engine': 'pdflatex',
                'return': 'pdf'
            }
            
            response = requests.post(api_url, data=payload, timeout=60)
            
            if response.status_code == 200 and response.headers.get('Content-Type') == 'application/pdf':
                with open(output_path, "wb") as f:
                    f.write(response.content)
                logger.info(f"✅ PDF généré avec succès via TexLive.net ({len(response.content)} bytes)")
                return True
            
            # If TexLive.net fails, try the old LatexOnline as a last resort
            logger.warning("TexLive.net failed, trying LatexOnline as last resort...")
            base_url = "https://latexonline.cc/compile"
            files = {'file': ('main.tex', latex_code, 'text/x-tex')}
            params = {'force': 'true', 'command': 'pdflatex'}
            response = requests.post(base_url, files=files, params=params, timeout=60)
            
            if response.status_code == 200 and len(response.content) > 500:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return True
                
            return False
        except Exception as e:
            logger.error(f"Online compilation error: {e}")
            return False

    def generate_cv_from_llm(self, user_profile: Dict[str, Any], experiences: List[Dict[str, Any]], template_name: str = "modern", feedback: str = None, session_id: str = None) -> (str, str): 
        """
        Generates a PDF CV.
        """
        if not self.llm:
            raise RuntimeError("GeneratorAgent non initialisé.")

        # Resolve photo_path (Keep logic from local_version)
        if "photo_path" in user_profile and user_profile["photo_path"]:
            photo_name = user_profile["photo_path"]
            avatar_map = {
                "man_laptop": "avatar_man_laptop.png",
                "woman_laptop": "avatar_woman_laptop.png",
                "man_coffee": "avatar_man_coffee.png",
                "woman_rocket": "avatar_woman_rocket.png",
                "marc_aurel": "the_marc_aurel.png",
                "avatar_femme": "avatar_femme.png"
            }
            if photo_name in avatar_map:
                photo_name = avatar_map[photo_name]

            candidates = [
                Path("frontend/src/assets") / photo_name,
                Path("data/img") / photo_name,
            ]
            resolved_path = None
            for cand in candidates:
                if cand.exists():
                    resolved_path = cand.resolve()
                    break
            
            if resolved_path:
                user_profile["photo_path"] = str(resolved_path).replace("\\", "/")
            else:
                user_profile["photo_path"] = ""

        safe_profile = sanitize_data_recursive(user_profile, skip_keys={"photo_path"})
        safe_experiences = sanitize_data_recursive(experiences)

        template_path = TEMPLATES_DIR / f"{template_name}.tex"
        if not template_path.exists():
            template_path = TEMPLATES_DIR / "modern.tex"

        cv_template_content = load_text(template_path)
        prompt_template = load_yaml("src/config/prompts/generator.yaml")['template']

        num_experiences = len(experiences)
        if num_experiences <= 3:
            verbosity_instruction = "HAUTE VERBOSITÉ REQUISE : étoffe chaque bullet point."
        else:
            verbosity_instruction = "OPTIMISATION 1 PAGE : sois concis pour les anciennes expériences."

        final_prompt = prompt_template.replace(
            "{{user_profile}}", json.dumps(safe_profile, indent=2, ensure_ascii=False)
        ).replace(
            "{{selected_experiences}}", json.dumps(safe_experiences, indent=2, ensure_ascii=False)
        ).replace(
            "{{cv_template}}", cv_template_content
        ).replace(
            "{{verbosity_instruction}}", verbosity_instruction
        )

        if feedback:
            final_prompt = f"NOTE PRÉCÉDENTE : {feedback}\n\n" + final_prompt

        try:
            generated_latex_code = self.llm.chat(final_prompt)
            generated_latex_code = clean_unicode_for_latex(generated_latex_code)
            generated_latex_code = self._clean_llm_output(generated_latex_code)
        except Exception as e:
            raise RuntimeError(f"L'IA a échoué: {e}")

        # Directory management
        unique_id = session_id or str(uuid.uuid4())
        session_dir = Path("outputs/generated_cvs") / unique_id
        session_dir.mkdir(parents=True, exist_ok=True)

        tex_path = session_dir / f"cv_{unique_id}.tex"
        pdf_path = session_dir / f"cv_{unique_id}.pdf"

        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(generated_latex_code)

        # --- MULTI-ENGINE COMPILATION ---
        compiled = False
        
        # 1. Try Tectonic (Recommended for Docker/Production)
        try:
            subprocess.run(["tectonic", "--version"], capture_output=True, check=True)
            logger.info("🚀 Compilation avec Tectonic...")
            cmd = ["tectonic", "-o", str(session_dir), str(tex_path)]
            subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if pdf_path.exists():
                compiled = True
        except:
            pass

        # 2. Try pdflatex (Local fallback)
        if not compiled:
            try:
                subprocess.run(["pdflatex", "--version"], capture_output=True, check=True)
                logger.info("🚀 Compilation avec pdflatex...")
                cmd = ["pdflatex", "-interaction=nonstopmode", f"-output-directory={session_dir}", str(tex_path)]
                subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if pdf_path.exists():
                    compiled = True
            except:
                pass

        # 3. Try Online APIs (Cloud fallback)
        if not compiled:
            compiled = self.compile_latex_online(generated_latex_code, pdf_path)

        if not compiled or not pdf_path.exists():
            raise RuntimeError("La compilation LaTeX a échoué sur tous les moteurs (Tectonic, Local et Online).")

        return str(pdf_path), str(tex_path)
