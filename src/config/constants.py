from pathlib import Path

# Define the absolute path to the project's root directory.
# This makes all file paths robust and independent of the current working directory.
# __file__ -> constants.py
# .parent -> config/
# .parent -> src/
# .parent -> project root
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

# Define all other paths relative to the project root.
KNOWLEDGE_BASE_PATH = ROOT_DIR / "data" / "knowledge_base.json"
EMBEDDINGS_DIR = ROOT_DIR / "data" / "embeddings"
JOB_OFFERS_DIR = ROOT_DIR / "data" / "exemples_offres" / "exemple_offre.txt"
GENERATED_CVS_DIR = ROOT_DIR / "outputs" / "generated_cvs"
TEMPLATES_DIR = ROOT_DIR / "src" / "templates"

MODEL_NAME = "text-embedding-3-small"