import os
import subprocess
import tempfile
import shutil
from typing import Tuple
from jinja2 import Environment

# Define a comprehensive set of dummy data that matches the template's expected variables.
# This data should ideally be clean and pre-escaped for LaTeX if direct rendering is intended,
# as the validator's primary role is now to check the template itself.
# For simplicity, we'll use a version that doesn't need external cleaning functions.
DUMMY_DATA = {
    "user": {
        "name": "John Doe",
        "title": "Software Engineer",
        "portfolio_url": "https://github.com/johndoe",
        "linkedin_url": "https://linkedin.com/in/johndoe",
        "email": "john.doe@email.com",
        "summary": "A dedicated software engineer with 5 years of experience in developing \& maintaining web applications using Python and JavaScript.",
        "education": [
            {
                "institution": "University of Technology",
                "period": "2015 - 2019",
                "degree": "Bachelor of Science in Computer Science",
                "mention": "Summa Cum Laude"
            }
        ],
        "skills": ["Python", "JavaScript", "React", "Node.js", "SQL", "Docker"],
        "soft_skills": [
            "Problem Solving", "Teamwork", "Communication", 
            "Adaptability", "Critical Thinking", "Creativity"
        ],
        "languages": [
            {"name": "French", "level": "Native"},
            {"name": "English", "level": "Fluent"}
        ]
    },
    "experiences": [
        {
            "title": "Senior Software Engineer",
            "company": "Tech Corp",
            "period": "2021 - Present",
            "description": "Led the development of a new microservices-based architecture, improving system scalability by 40\%. Mentored junior developers."
        },
        {
            "title": "Software Engineer",
            "company": "Innovate LLC",
            "period": "2019 - 2021",
            "description": "Developed and maintained features for a large-scale e-commerce platform. Contributed to a 20\% reduction in page load times."
        }
    ]
}

def validate_latex_template(template_path: str) -> Tuple[bool, str]:
    """
    Validates a Jinja2-LaTeX template by rendering it with dummy data and compiling it.
    This validator now focuses on the template's structure and its ability to compile
    when filled with reasonable, pre-escaped data, given the LLM generates the final LaTeX.

    Args:
        template_path: The path to the .tex template file.

    Returns:
        A tuple containing a boolean indicating success and a message.
    """
    if not os.path.exists(template_path):
        return False, f"Error: Template file not found at '{template_path}'"

    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
    except Exception as e:
        return False, f"Error reading template file: {e}"

    # Render the template with dummy data
    try:
        # Configure Jinja2 environment for custom delimiters as found in the template
        env = Environment(
            block_start_string='(%',
            block_end_string='%)',
            variable_start_string='((',
            variable_end_string='))',
            comment_start_string='(#{',
            comment_end_string='}#)'
        )
        template = env.from_string(template_content)
        
        # Prepare context assuming LLM will provide user and experiences data formatted for template
        context = {
            "user": DUMMY_DATA["user"],
            "experiences": DUMMY_DATA["experiences"]
        }

        rendered_latex = template.render(**context)
    except Exception as e:
        return False, f"Jinja2 rendering failed: {e}"

    # Compile the rendered LaTeX file
    temp_dir = tempfile.mkdtemp()
    temp_tex_path = os.path.join(temp_dir, "validation_check.tex")

    with open(temp_tex_path, 'w', encoding='utf-8') as f:
        f.write(rendered_latex)

    command = [
        "pdflatex",
        "-interaction=nonstopmode",
        "-output-directory",
        temp_dir,
        temp_tex_path
    ]

    try:
        subprocess.run(
            command,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        message = "Success: LaTeX template compiled without errors with dummy data."
        is_valid = True
    except FileNotFoundError:
        message = "Error: 'pdflatex' command not found. Is a LaTeX distribution (like MiKTeX or TeX Live) installed and in your system's PATH?"
        is_valid = False
    except subprocess.CalledProcessError:
        log_file_path = os.path.join(temp_dir, "validation_check.log")
        if os.path.exists(log_file_path):
            with open(log_file_path, 'r', encoding='utf-8') as log_file:
                log_content = log_file.read()
            error_lines = [line for line in log_content.splitlines() if line.startswith('!')]
            if error_lines:
                message = f"LaTeX compilation failed. First error found: {error_lines[0]}"
            else:
                message = "LaTeX compilation failed. Check 'validation_check.log' for details."
        else:
            message = "LaTeX compilation failed, but no log file was found."
        is_valid = False
    finally:
        shutil.rmtree(temp_dir)

    return is_valid, message

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    template_to_check = os.path.join(project_root, "src", "interfaces", "prompts", "cv_template.tex")
    
    print(f"Validating template: {template_to_check}")
    valid, msg = validate_latex_template(template_to_check)
    print(msg)

    if not valid:
        exit(1)
