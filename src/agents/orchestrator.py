from src.core.knowledge_base import load_knowledge_base
from src.config.constants import KNOWLEDGE_BASE_PATH

class OrchestratorAgent:
    def __init__(self):
        self.kb = load_knowledge_base(KNOWLEDGE_BASE_PATH)

    def run(self):
        print("Bienvenue sur reZume !")
        print(f"Profil chargé : {self.kb.name}")
