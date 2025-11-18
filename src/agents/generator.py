# src/agents/generator.py
import os
import json
import subprocess
from jinja2 import Environment, FileSystemLoader
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
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Render template with Jinja2 using custom delimiters
        env = Environment(
            loader=FileSystemLoader(os.path.dirname(template_path)),
            block_start_string='(%',
            block_end_string='%)',
            variable_start_string='(( ',
            variable_end_string=' ))',
            comment_start_string='(#',
            comment_end_string='#)'
        )

        template_name = os.path.basename(template_path)
        tpl = env.get_template(template_name)

        context = {
            "skills": user_data.get("skills", []),
            "experiences": selected_experiences,
            "user": user_data
        }

        rendered = tpl.render(**context)

        # Optional LLM rewrite
        if self.llm:
            prompt = self.prompt_cfg["template"]
            prompt = prompt.replace("{{user_profile}}", json.dumps(user_data, ensure_ascii=False))
            prompt = prompt.replace("{{selected_experiences}}", json.dumps(selected_experiences, ensure_ascii=False))
            prompt = prompt.replace("{{cv_template}}", rendered)
            resp = self.llm.chat(prompt)
            final_text = resp
        else:
            final_text = rendered

        # Determine output format based on template extension
        if template_path.endswith(".tex"):
            base_output_name = os.path.splitext(os.path.basename(output_path))[0]
            tex_out = os.path.join(os.path.dirname(output_path), f"{base_output_name}.tex")
            pdf_out = os.path.join(os.path.dirname(output_path), f"{base_output_name}.pdf")

            # write LaTeX
            with open(tex_out, "w", encoding="utf-8") as f:
                f.write(final_text)

            # Compile LaTeX → PDF
            try:
                subprocess.run(["pdflatex", "-interaction=nonstopmode", "-output-directory",
                                os.path.dirname(output_path), tex_out],
                                check=True, capture_output=True)
                subprocess.run(["pdflatex", "-interaction=nonstopmode", "-output-directory",
                                os.path.dirname(output_path), tex_out],
                                check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                print("LaTeX compilation failed:")
                print("STDOUT:", e.stdout.decode())
                print("STDERR:", e.stderr.decode())
                raise RuntimeError("pdflatex error")

            # Clean temp files
            for ext in ['.aux', '.log', '.out', '.toc', '.synctex.gz']:
                f = tex_out.replace(".tex", ext)
                if os.path.exists(f):
                    os.remove(f)

            return pdf_out

        # default text output
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_text)

        return output_path
