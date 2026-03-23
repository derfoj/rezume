# src/agents/generator.py
import os
import json
import logging
import uuid
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
        "ʳ": "r",
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

    # We use a mapping and replace in one go or use a strategy that doesn't re-escape
    # The safest way is to use a regex or a very specific order.
    # Here we escape the special chars EXCEPT backslash first, then backslash.
    # Actually, the standard way is to use a map and a regex.
    
    import re
    map = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
        "\\": r"\textbackslash{}"
    }
    
    # Regex to match any of the keys in map (escaping backslash for regex)
    regex = re.compile("|".join(re.escape(k) for k in map.keys()))
    return regex.sub(lambda m: map[m.group(0)], text)

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
    An agent responsible for generating the final LaTeX CV source code.
    The compilation is now handled by the frontend via SwiftLaTeX (WASM).
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

    def generate_latex_source(self, user_profile: Dict[str, Any], experiences: List[Dict[str, Any]], template_name: str = "modern", feedback: str = None, session_id: str = None) -> str: 
        """
        Generates LaTeX source code.
        """
        if not self.llm:
            raise RuntimeError("GeneratorAgent non initialisé.")

        # Always use standard path for the photo in LaTeX code
        # The frontend SwiftLaTeX component will inject the actual image into this virtual path.
        if user_profile.get("photo_path") or user_profile.get("photo_cv"):
            user_profile["photo_path"] = "photo_cv.png"
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
            
            # Directory management for logging/audit
            unique_id = session_id or str(uuid.uuid4())
            session_dir = Path("outputs/generated_cvs") / unique_id
            session_dir.mkdir(parents=True, exist_ok=True)
            tex_path = session_dir / f"cv_{unique_id}.tex"
            with open(tex_path, "w", encoding="utf-8") as f:
                f.write(generated_latex_code)
                
            return generated_latex_code
        except Exception as e:
            raise RuntimeError(f"L'IA a échoué: {e}")
