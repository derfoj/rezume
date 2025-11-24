# src/agents/generator.py
import os
import json
import subprocess
import uuid
from pathlib import Path
from typing import List, Dict, Any

from src.core.utils import load_yaml, load_text
from src.core.llm_provider import get_llm
from src.config.constants import CV_TEMPLATE_PATH

class GeneratorAgent:
    """
    An agent responsible for generating the final LaTeX CV by calling an LLM
    with a complete context, then compiling the result to PDF.
    """
    def __init__(self):
        try:
            self.llm = get_llm()
            print("✅ GeneratorAgent prêt et connecté au LLM.")
        except Exception as e:
            self.llm = None
            print(f"❌ Erreur lors de l'init du GeneratorAgent: {e}")

    def _clean_llm_output(self, latex_code: str) -> str:
        """Strips markdown code blocks and leading/trailing whitespace."""
        code = latex_code.strip()
        if code.startswith("```latex"):
            code = code[len("```latex"):
].strip()
        if code.endswith("```"):
            code = code[:-len("```")].strip()
        
        # Ensure it starts with \documentclass
        if not code.startswith(r"\documentclass"):
            return latex_code # Return original if cleaning is likely wrong
        
        return code

    def generate_cv_from_llm(self, user_profile: Dict[str, Any], experiences: List[Dict[str, Any]]) -> (str, str):
        """
        Generates a PDF CV using the LLM-as-a-template-engine approach.
        
        Returns:
            A tuple of (pdf_path, tex_path).
        """
        if not self.llm:
            raise RuntimeError("GeneratorAgent non initialisé, impossible de générer le CV.")

        print("🔹 Préparation du contexte pour la génération par LLM...")
        cv_template_content = load_text(CV_TEMPLATE_PATH)
        
        prompt_template = load_yaml("src/config/prompts/generator.yaml")['template']
        
        # Use .replace() for safety with LaTeX syntax
        final_prompt = prompt_template.replace(
            "{{user_profile}}", json.dumps(user_profile, indent=2, ensure_ascii=False)
        ).replace(
            "{{selected_experiences}}", json.dumps(experiences, indent=2, ensure_ascii=False)
        ).replace(
            "{{cv_template}}", cv_template_content
        )

        print("🔹 Appel du LLM pour la génération du code LaTeX...")
        try:
            generated_latex_code = self.llm.chat(final_prompt)
            generated_latex_code = self._clean_llm_output(generated_latex_code)
        except Exception as e:
            print(f"❌ Erreur lors de l'appel au LLM: {e}")
            raise RuntimeError(f"L'appel au service IA a échoué: {e}")
        
        print("⚙️ Compilation du PDF en cours...")
        
        output_dir = Path(__file__).resolve().parent.parent.parent / "outputs" / "generated_cvs"
        os.makedirs(output_dir, exist_ok=True)
        
        unique_id = uuid.uuid4()
        base_name = f"rezume_llm_{unique_id}"
        tex_path = output_dir / f"{base_name}.tex"
        pdf_path = output_dir / f"{base_name}.pdf"

        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(generated_latex_code)

        cmd = ["pdflatex", "-interaction=nonstopmode", f"-output-directory={str(output_dir)}", str(tex_path)]
        try:
            # We run compilation twice. We don't check for exit code because pdflatex
            # can return non-zero for warnings even if a PDF is generated.
            subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        except FileNotFoundError:
            raise RuntimeError("pdflatex introuvable. Assurez-vous qu'une distribution LaTeX est installée.")
        
        # Instead of checking the exit code, we check if the PDF was actually created.
        if not pdf_path.exists():
            log_file = tex_path.with_suffix(".log")
            log_content = log_file.read_text(encoding='utf-8', errors='ignore') if log_file.exists() else "Fichier log non trouvé."
            print(f"❌ Erreur de compilation LaTeX. Le PDF n'a pas été créé. Log:\n{log_content[-1500:]}")
            raise RuntimeError("La compilation LaTeX a échoué (aucun PDF produit).")
        
        return str(pdf_path), str(tex_path)