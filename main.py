import sys
from dotenv import load_dotenv
from src.agents.orchestrator import OrchestratorAgent
from src.core.latex_validator import validate_latex_template
from src.config.constants import CV_TEMPLATE_PATH # Assuming constants are well-defined

def main():
    """Main execution function."""
    # Check for the --validate flag
    if "--validate" in sys.argv:
        print("Running LaTeX template validation...")
        is_valid, message = validate_latex_template(CV_TEMPLATE_PATH)
        print(message)
        # Exit with a status code indicating success or failure
        sys.exit(0 if is_valid else 1)

    # If no validation flag, run the main pipeline
    load_dotenv()
    orchestrator = OrchestratorAgent()
    out = orchestrator.run_pipeline()
    print("Done. Output:", out)


if __name__ == "__main__":
    main()
