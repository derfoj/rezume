# src/agents/generator.py
import os
import json
import subprocess
from src.core.utils import load_yaml, load_text
from src.core.llm_provider import get_llm

class GeneratorAgent:
    def __init__(self, prompt_path: str):
        self.prompt_cfg = load_yaml(prompt_path)
        try:
            self.llm = get_llm()
        except NotImplementedError:
            self.llm = None

    def generate_cv(self, user_data: dict, selected_experiences: list, template_path: str, output_path: str) -> str:
        """
        Generates the full LaTeX CV by calling the LLM with the complete context.
        """
        if not self.llm:
            raise EnvironmentError("LLM not initialized. Cannot generate CV.")

        print("🔹 Préparation du contexte pour l'IA générative...")
        
        # 1. Charger le contenu du template LaTeX
        cv_template_content = load_text(template_path)

        # 2. Préparer les données d'entrée pour le prompt
        # L'IA est responsable de la génération et de l'échappement des caractères LaTeX.
        prompt_context = {
            "user_profile": json.dumps(user_data, indent=2, ensure_ascii=False),
            "selected_experiences": json.dumps(selected_experiences, indent=2, ensure_ascii=False),
            "cv_template": cv_template_content
        }

        # 3. Construire le prompt final en remplaçant les placeholders manuellement
        final_prompt = self.prompt_cfg['template']
        final_prompt = final_prompt.replace("{{user_profile}}", prompt_context["user_profile"])
        final_prompt = final_prompt.replace("{{selected_experiences}}", prompt_context["selected_experiences"])
        final_prompt = final_prompt.replace("{{cv_template}}", prompt_context["cv_template"])

        print("🔹 Appel de l'IA pour la génération du contenu du CV...")
        # 4. Appeler l'IA pour générer le code LaTeX
        generated_latex_code = self.llm.chat(final_prompt)

        # Nettoyage simple pour s'assurer que le code est pur
        generated_latex_code = generated_latex_code.strip()
        if generated_latex_code.startswith("```latex"):
            generated_latex_code = generated_latex_code[len("```latex"):].strip()
        if generated_latex_code.endswith("```"):
            generated_latex_code = generated_latex_code[:-len("```")].strip()
        
        print("🔹 Compilation du PDF final...")
        # 5. Compilation du PDF
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        base_output_name = os.path.splitext(os.path.basename(output_path))[0]
        output_dir = os.path.abspath(os.path.dirname(output_path))
        tex_out = os.path.join(output_dir, f"{base_output_name}.tex")
        pdf_out = os.path.join(output_dir, f"{base_output_name}.pdf")

        with open(tex_out, "w", encoding="utf-8") as f:
            f.write(generated_latex_code)

        cmd = [
            "pdflatex",
            "-interaction=nonstopmode",
            f"-output-directory={output_dir}",
            tex_out
        ]

        try:
            # On compile deux fois pour s'assurer que la mise en page est bonne
            subprocess.run(cmd, check=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            subprocess.run(cmd, check=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        except subprocess.CalledProcessError as e:
            print("\n ERREUR CRITIQUE LATEX !")
            print("Voici les dernières lignes du journal d'erreur (log) :")
            print("-" * 30)
            log_file_path = os.path.join(output_dir, f"{base_output_name}.log")
            if os.path.exists(log_file_path):
                with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as log_f:
                    print("".join(log_f.readlines()[-20:]))
            else:
                print("Fichier log non trouvé.")
            print("-" * 30)
            raise RuntimeError(f"Échec de la compilation pdflatex. Vérifiez le fichier {tex_out} pour les erreurs.")

        # Nettoyage des fichiers temporaires
        for ext in ['.aux', '.log', '.out', '.toc']:
            temp_file = os.path.join(output_dir, f"{base_output_name}{ext}")
            if os.path.exists(temp_file):
                os.remove(temp_file)

        return pdf_out
