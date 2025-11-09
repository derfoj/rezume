from src.agents.orchestrator import OrchestratorAgent

def main():
    orchestrator = OrchestratorAgent(
        offer_path="data/exemples_offres/exemple_offre.txt",
        knowledge_path="data/knowledge_base.json",
        template_path="src/interfaces/prompts/cv_template.txt",
        output_dir="outputs/generated_cvs"
    )
    generated = orchestrator.run_pipeline()
    print("Done. Output:", generated)

if __name__ == "__main__":
    main()
