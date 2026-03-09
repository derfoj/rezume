import os
import re
import subprocess
import logging
from pathlib import Path
from typing import Tuple, List, Dict, Any

logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """Normalize text for searching."""
    return re.sub(r'\s+', ' ', text).strip().lower()

def check_page_count(tex_path: str, output_dir: str) -> Tuple[int, str]:
    """
    Tries to compile locally if pdflatex is present.
    Returns (page_count, log_content).
    """
    cmd = ["pdflatex", "-interaction=nonstopmode", f"-output-directory={output_dir}", str(tex_path)]
    
    try:
        # Check if pdflatex exists
        subprocess.run(["pdflatex", "--version"], capture_output=True, check=True)
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        log_file = Path(output_dir) / Path(tex_path).with_suffix('.log').name
        if log_file.exists():
            log_content = log_file.read_text(encoding='utf-8', errors='ignore')
            match = re.search(r'Output written on .*? \((\d+) page', log_content)
            if match:
                return int(match.group(1)), log_content
        return 0, "Compilation failed to produce page count."
    except:
        # If pdflatex is missing (common on Render), we skip this check
        return -1, "pdflatex not found. Skipping local page count check."

def check_content_rules(tex_content: str, target_company: str = None) -> List[str]:
    warnings = []
    placeholders = ["lorem ipsum", "[date]", "[company]"]
    for p in placeholders:
        if p in tex_content.lower():
            warnings.append(f"⚠️  Placeholder trouvé : '{p}'")
    return warnings

def validate_cv(tex_path: str, target_company: str = None) -> Dict[str, Any]:
    path = Path(tex_path).resolve()
    if not path.exists():
        return {"valid": False, "warnings": ["Fichier non trouvé"]}
        
    content = path.read_text(encoding='utf-8', errors='ignore')
    warnings = check_content_rules(content, target_company)
    
    pages, _ = check_page_count(path, str(path.parent))
    
    page_status = "ok"
    if pages > 1:
        warnings.append(f"❌ Le CV fait {pages} pages (Limite: 1)")
        page_status = "error"
    elif pages == -1:
        page_status = "skipped" # pdflatex missing, we allow it
        
    return {
        "valid": page_status != "error",
        "page_count": max(0, pages),
        "page_status": page_status,
        "warnings": warnings
    }
