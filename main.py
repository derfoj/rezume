# main.py
from dotenv import load_dotenv
from src.agents.orchestrator import OrchestratorAgent

if __name__ == "__main__":
    load_dotenv() 
    orchestrator = OrchestratorAgent()
    out = orchestrator.run_pipeline()
    print("Done. Output:", out)
