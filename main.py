from src.agents.orchestrator import OrchestratorAgent
from src.config.constants import *

def main():
    orchestrator = OrchestratorAgent(
        offer_path=JOB_OFFERS_DIR ,
        knowledge_path=KNOWLEDGE_BASE_PATH,
        template_path=TEMPLATE_PATH,
        output_dir=GENERATED_CVS_DIR ,
    )
    generated = orchestrator.run_pipeline()
    print("Done. Output:", generated)

if __name__ == "__main__":
    main()
