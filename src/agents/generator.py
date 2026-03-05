# src/agents/generator.py
import os
import json
import subprocess
import uuid
from pathlib import Path
from typing import List, Dict, Any

from src.core.utils import load_yaml, load_text
from src.core.llm_provider import get_llm
from src.config.constants import TEMPLATES_DIR

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
            print(f"✅ GeneratorAgent prêt ({provider or 'default'}/{model or 'default'}).")
        except Exception as e:
            self.llm = None
            print(f"❌ Erreur lors de l'init du GeneratorAgent: {e}")

    def _clean_llm_output(self, latex_code: str) -> str:
        """
        Robustly extracts LaTeX code from LLM output, handling markdown blocks 
        and conversational text.
        """
        import re
        
        # Pattern to find content inside ```latex ... ``` or ``` ... ```
        # Flags: dotall to match newlines
        match = re.search(r"```(?:latex)?\s*(.*?)\s*```", latex_code, re.DOTALL | re.IGNORECASE)
        
        if match:
            clean_code = match.group(1).strip()
            # Double check if it looks like latex
            if clean_code.startswith("\\documentclass"):
                return clean_code
        
        # Fallback: Look for start of documentclass
        if not match:
            start_idx = latex_code.find("\\documentclass")
            if start_idx != -1:
                latex_code = latex_code[start_idx:]
            else:
                # If no documentclass, maybe it's just the body? Unlikely for this agent.
                pass
        else:
            latex_code = match.group(1).strip()

        # Final cleanup: Remove anything after \end{document}
        end_marker = "\\end{document}"
        end_idx = latex_code.find(end_marker)
        if end_idx != -1:
            latex_code = latex_code[:end_idx + len(end_marker)]
            
        return latex_code.strip()





    def generate_cv_from_llm(self, user_profile: Dict[str, Any], experiences: List[Dict[str, Any]], template_name: str = "modern", feedback: str = None, session_dir: Path = None) -> (str, str):
        """
        Generates a PDF CV using the LLM-as-a-template-engine approach.
        
        Args:
            feedback: Optional string containing specific instructions to fix errors from a previous run.
            session_dir: Optional Path to an existing session directory (for retries).
        
        Returns:
            A tuple of (pdf_path, tex_path).
        """
        if not self.llm:
            raise RuntimeError("GeneratorAgent non initialisé, impossible de générer le CV.")

        print(f"🔹 Préparation du contexte pour la génération par LLM (Template: {template_name})...")
        
        # --- SECURITY FIX: Sanitize Input Data ---
        
        # Resolve photo_path to absolute path for LaTeX
        if "photo_path" in user_profile and user_profile["photo_path"]:
            photo_name = user_profile["photo_path"]
            
            # Map predefined avatar IDs to filenames
            avatar_map = {
                "man_laptop": "avatar_man_laptop.png",
                "woman_laptop": "avatar_woman_laptop.png",
                "man_coffee": "avatar_man_coffee.png",
                "woman_rocket": "avatar_woman_rocket.png",
                "marc_aurel": "the_marc_aurel.png",
                "avatar_femme": "avatar_femme.png"
            }
            
            # Use mapped filename if it's a known ID, otherwise keep original (for uploads)
            if photo_name in avatar_map:
                photo_name = avatar_map[photo_name]

            # Potential locations for images
            candidates = [
                Path(__file__).resolve().parent.parent.parent / "frontend" / "src" / "assets" / photo_name,
                Path(__file__).resolve().parent.parent.parent / "data" / "img" / photo_name, # Handles uploads/filename
            ]
            
            resolved_path = None
            for cand in candidates:
                if cand.exists():
                    resolved_path = cand
                    break
            
            if resolved_path:
                # LaTeX requires forward slashes even on Windows
                user_profile["photo_path"] = str(resolved_path).replace("\\", "/")
            else:
                # If file not found, remove it to avoid LaTeX errors or set to empty string
                print(f"⚠️ Image '{photo_name}' introuvable. Le CV sera généré sans photo.")
                user_profile["photo_path"] = ""

        safe_profile = sanitize_data_recursive(user_profile, skip_keys={"photo_path"})
        safe_experiences = sanitize_data_recursive(experiences)
        # -----------------------------------------

        template_path = TEMPLATES_DIR / f"{template_name}.tex"
        if not template_path.exists():
            print(f"⚠️ Template '{template_name}' introuvable. Fallback sur 'modern'.")
            template_path = TEMPLATES_DIR / "modern.tex"

        cv_template_content = load_text(template_path)
        
        prompt_template = load_yaml("src/config/prompts/generator.yaml")['template']

        # Determine verbosity based on experience count
        num_experiences = len(experiences)
        if num_experiences <= 3:
            verbosity_instruction = "HAUTE VERBOSITÉ REQUISE : Le candidat a 3 expériences sélectionnées (3 ou moins). étoffe chaque bullet point. Détaille un peu le contexte, la méthodologie, les défis techniques et les résultats. Chaque expérience doit occuper un espace visuel raisonnable conséquent pour éviter que le CV ne paraisse vide. Ne sois PAS concis."
        elif num_experiences >= 4:
            verbosity_instruction = "OPTIMISATION INTELLIGENTE (OBJECTIF 1 PAGE) : Le candidat a plusieurs expériences. Tu DOIS faire tenir le CV sur UNE SEULE page. Pour cela, applique cette stratégie de condensation : sois DÉTAILLÉ pour les 2 expériences les plus récentes (3-4 bullet points percutants), mais sois TRÈS CONCIS pour les expériences plus anciennes (1-2 bullet points synthétiques). Cherche l'équilibre parfait entre densité d'information et gain de place."
        else:
            verbosity_instruction = "VERBOSITÉ STANDARD : Sois concis, direct et percutant. Privilégie la densité d'information à la longueur."
        
        # --- Template Specific Rules ---
        if template_name == "modern":
            verbosity_instruction += "\n\nRÈGLE SPÉCIALE MODERN : Pour la section 'Compétences' (Expertise Technique), tu DOIS sélectionner UNIQUEMENT les 12 compétences les plus pertinentes et percutantes. Ne liste PAS tout. La liste doit être lisible et aérée."

        # Use .replace() for safety with LaTeX syntax
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
            print(f"⚠️ Correction demandée : {feedback}")
            final_prompt += f"\n\nATTENTION : Une version précédente a été rejetée pour les raisons suivantes :\n{feedback}\nTu DOIS corriger ces erreurs impérativement dans cette nouvelle version."

        print("🔹 Appel du LLM pour la génération du code LaTeX...")
        try:
            generated_latex_code = self.llm.chat(final_prompt)
            # Pre-clean Unicode characters that might break compilation
            generated_latex_code = clean_unicode_for_latex(generated_latex_code)
            generated_latex_code = self._clean_llm_output(generated_latex_code)
        except Exception as e:
            print(f"❌ Erreur lors de l'appel au LLM: {e}")
            raise RuntimeError(f"L'appel au service IA a échoué: {e}")
        
        print("⚙️ Compilation du PDF en cours...")
        
        if not session_dir:
            # Create a unique directory for this generation session
            unique_id = uuid.uuid4()
            base_name = f"rezume_llm_{unique_id}"
            session_dir = Path(__file__).resolve().parent.parent.parent / "outputs" / "generated_cvs" / base_name
            os.makedirs(session_dir, exist_ok=True)
        else:
            base_name = session_dir.name
        
        # Ensure session_dir is a Path object
        session_dir = Path(session_dir)

        tex_path = session_dir / f"{base_name}.tex"
        pdf_path = session_dir / f"{base_name}.pdf"

        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(generated_latex_code)

        cmd = ["pdflatex", "-interaction=nonstopmode", f"-output-directory={str(session_dir)}", str(tex_path)]
        try:
            # We run compilation twice.
            subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        except FileNotFoundError:
            raise RuntimeError("pdflatex introuvable. Assurez-vous qu'une distribution LaTeX est installée.")
        
        if not pdf_path.exists():
            log_file = tex_path.with_suffix(".log")
            log_content = log_file.read_text(encoding='utf-8', errors='ignore') if log_file.exists() else "Fichier log non trouvé."
            print(f"❌ Erreur de compilation LaTeX. Log:\n{log_content[-1500:]}")
            raise RuntimeError("La compilation LaTeX a échoué (aucun PDF produit).")
        
        return str(pdf_path), str(tex_path)
