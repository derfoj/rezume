import json
from src.config.schema_definitions import KnowledgeBase
from src.config.constants import KNOWLEDGE_BASE_PATH

def load_knowledge_base(path: str = KNOWLEDGE_BASE_PATH) -> KnowledgeBase:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return KnowledgeBase(**data)
