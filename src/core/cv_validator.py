import os
import re
import subprocess
from pathlib import Path
from typing import Tuple, List, Dict, Any

def clean_text(text: str) -> str:
    """Normalize text for searching."""
    return re.sub(r'\s+', ' ', text).strip().lower()

def check_page_count(tex_path: str, output_dir: str) -> Tuple[int, str]:
    """
    Compiles the LaTeX file to check the page count.
    Returns (page_count, log_content).
    """
    cmd = [
        "pdflatex", 
        "-interaction=nonstopmode", 
        f"-output-directory={output_dir}", 
        str(tex_path)
    ]
    
    try:
        # Run compilation
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        # Read the log file
        log_file = Path(output_dir) / Path(tex_path).with_suffix('.log').name
        if log_file.exists():
            log_content = log_file.read_text(encoding='utf-8', errors='ignore')
            
            # Look for "Output written on ... (N pages, ...)"
            match = re.search(r'Output written on .*? \((\d+) page', log_content)
            if match:
                return int(match.group(1)), log_content
            
        return 0, result.stdout + result.stderr
        
    except Exception as e:
        return 0, str(e)

def check_content_rules(tex_content: str, target_company: str = None) -> List[str]:
    """
    Checks for forbidden patterns and content rules.
    """
    warnings = []
    
    # Rule: Target Company Confusion
    if target_company:
        tc_clean = clean_text(target_company)
        content_clean = clean_text(tex_content)
        # Avoid matching the company name if it's in the objective/header.
        # Ideally we'd parse the structure, but a simple check is a good start.
        if tc_clean in content_clean:
             warnings.append(f"⚠️  Target company '{target_company}' found in LaTeX. Verify it's not falsely listed as an employer.")

    # Rule: Placeholder text
    placeholders = ["lorem ipsum", "insert here", "[date]", "[company]"]
    for p in placeholders:
        if p in tex_content.lower():
            warnings.append(f"⚠️  Placeholder found: '{p}'")
            
    # Rule: Empty sections (heuristic)
    if "\resumeSubHeadingListStart" in tex_content and "\resumeSubHeadingListEnd" in tex_content:
        # Check if empty between them
        pattern = r'\\resumeSubHeadingListStart\s*\\resumeSubHeadingListEnd'
        if re.search(pattern, tex_content):
            warnings.append("⚠️  Found empty experience/education list.")

    return warnings

def validate_cv(tex_path: str, target_company: str = None) -> Dict[str, Any]:
    """
    Runs full validation on the generated CV.
    Returns a dictionary with status and warnings.
    """
    path = Path(tex_path).resolve()
    if not path.exists():
        return {"valid": False, "errors": ["File not found"]}
        
    content = path.read_text(encoding='utf-8', errors='ignore')
    warnings = check_content_rules(content, target_company)
    
    # Check page count
    output_dir = str(path.parent)
    pages, _ = check_page_count(path, output_dir)
    
    page_status = "ok"
    if pages > 1:
        warnings.append(f"❌ Page count violation: {pages} pages (Limit: 1)")
        page_status = "error"
    elif pages == 0:
        warnings.append("❌ Compilation failed or page count could not be determined.")
        page_status = "error"
        
    return {
        "valid": len(warnings) == 0,
        "page_count": pages,
        "page_status": page_status,
        "warnings": warnings
    }
