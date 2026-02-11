import argparse
import sys
import os
from pathlib import Path

# Add project root to path to import src
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.core.cv_validator import validate_cv

def main():
    parser = argparse.ArgumentParser(description="Check CV LaTeX compliance.")
    parser.add_argument("tex_file", help="Path to the .tex file to check.")
    parser.add_argument("--company", help="Name of the target company (to check for hallucinations).", default=None)
    
    args = parser.parse_args()
    
    print(f"🚀 Checking {args.tex_file}...")
    result = validate_cv(args.tex_file, args.company)
    
    if result["warnings"]:
        print("\n⚠️  ISSUES FOUND:")
        for w in result["warnings"]:
            print(w)
    else:
        print("\n✅  ALL CHECKS PASSED. CV is compliant.")
        
    print(f"\nDetails: {result['page_count']} page(s).")

if __name__ == "__main__":
    main()