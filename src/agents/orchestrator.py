# src/agents/orchestrator.py
import os
from src.core.utils import load_json, load_text, ensure_dir, load_yaml
from src.agents.parser import ParserAgent
from src.core.vector_store import build_vector_store, search_vector_store
from src.agents.generator import GeneratorAgent
from src.config.constants import EMBEDDINGS_DIR

class OrchestratorAgent:
    def __init__(self, settings_path: str = "src/config/settings.yaml"):
        cfg = load_yaml(settings_path)
        paths = cfg.get("paths", {})

        self.offer_path = paths.get("offers")
        self.knowledge_path = paths.get("knowledge_base")
        self.template_path = paths.get("templates")
        self.output_dir = paths.get("output_dir")

        self.index_name = "kb_index"

        parser_prompt_path = paths.get("parser_prompt")
        generator_prompt_path = paths.get("generator_prompt")

        self.parser = ParserAgent(prompt_path=parser_prompt_path)
        self.generator = GeneratorAgent(prompt_path=generator_prompt_path)

        ensure_dir(self.output_dir)

    def _ensure_vector_store(self):
        index_path = os.path.join(EMBEDDINGS_DIR, f"{self.index_name}.faiss")
        if not os.path.exists(index_path):
            print(f"Building vector store: {index_path}")
            user_data = load_json(self.knowledge_path)
            experiences = user_data.get("experiences", [])
            if experiences:
                build_vector_store(experiences, self.index_name)
            else:
                print("⚠ Aucune expérience trouvée dans la base de connaissances → impossible de créer un index.")

    def run_pipeline(self) -> str:
        if not os.path.exists(self.offer_path):
            raise FileNotFoundError(self.offer_path)

        if not os.path.exists(self.knowledge_path):
            raise FileNotFoundError(self.knowledge_path)

        if not os.path.exists(self.template_path):
            raise FileNotFoundError(self.template_path)

        print("\n🔹 Étape 1 — Analyse de l'offre d'emploi...")
        offer_text = load_text(self.offer_path)
        parsed = self.parser.extract_information(offer_text)

        print("→ skills:", parsed.get("skills", []))
        print("→ missions:", parsed.get("missions", [])[:3])
        print("→ values:", parsed.get("values", []))

        print("\n🔹 Étape 2 — Recherche sémantique...")
        self._ensure_vector_store()

        query = f"Skills: {', '.join(parsed.get('skills', []))}. Missions: {' '.join(parsed.get('missions', []))}"
        selected = search_vector_store(query, self.index_name)

        print(f"→ {len(selected)} experiences selected")

        print("\n🔹 Étape 3 — Création du CV...")
        user_data = load_json(self.knowledge_path)

        # Generate a unique filename with a timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = os.path.join(self.output_dir, f"cv_generated_{timestamp}.pdf")
        
        result_path = self.generator.generate_cv(user_data, selected, self.template_path, out_path)

        print(f"\n CV successfully generated → {result_path}\n")
        return result_path

