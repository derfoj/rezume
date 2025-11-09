import os
from src.core.utils import load_json, load_offer_text, ensure_dir
from src.agents.parser import ParserAgent
from src.agents.optimizer import OptimizerAgent
from src.agents.generator import GeneratorAgent

class OrchestratorAgent:
    def __init__(self,
                 offer_path: str = "data/exemples_offres/exemple_offre.txt",
                 knowledge_path: str = "data/knowledge_base.json",
                 template_path: str = "src/interfaces/prompts/cv_template.txt",
                 output_dir: str = "outputs/generated_cvs"):
        self.offer_path = offer_path
        self.knowledge_path = knowledge_path
        self.template_path = template_path
        self.output_dir = output_dir

        self.parser = ParserAgent()
        self.optimizer = OptimizerAgent()
        self.generator = GeneratorAgent()

        ensure_dir(self.output_dir)

    def run_pipeline(self) -> str:
        # Vérification des fichiers nécessaires
        if not os.path.exists(self.offer_path):
            raise FileNotFoundError(f"Offer file missing: {self.offer_path}")
        if not os.path.exists(self.knowledge_path):
            raise FileNotFoundError(f"Knowledge base missing: {self.knowledge_path}")
        if not os.path.exists(self.template_path):
            raise FileNotFoundError(f"Template missing: {self.template_path}")

        # Chargement des données
        user_data = load_json(self.knowledge_path)
        offer_text = load_offer_text(self.offer_path)

        print("\n🔹 Étape 1 : Parsing / extraction...")
        parsed = self.parser.extract_information(offer_text)
        print("   → skills:", parsed.get("skills", [])[:3])
        missions = parsed.get("missions", [])
        print("   → missions:", missions[:3] if isinstance(missions, list) else [])
        print("   → valeurs:", parsed.get("values", [])[:3])

        print("\n🔹 Étape 2 : Sélection des expériences pertinentes...")
        selected = self.optimizer.select_relevant_experiences(user_data, parsed)
        print("   → expériences sélectionnées:", [e.get("title") for e in selected])

        print("\n🔹 Étape 3 : Génération du CV...")
        out_path = os.path.join(self.output_dir, "cv_generated.txt")
        result_path = self.generator.generate_cv(user_data, selected, self.template_path, out_path)

        print(f"\n CV généré avec succès → {result_path}\n")
        return result_path
