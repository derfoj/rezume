import os, json, yaml, re

def ensure_dir(path: str):
    if not os.path.exists(path):
        os.makedirs(path)

def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_text(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def load_yaml(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def sanitize_input(text: str) -> str:
    """
    Prevents Prompt Injections and malicious text.
    Removes potentially dangerous keywords.
    """
    if not text:
        return ""
    # Basic cleaning
    text = text.strip()
    # List of keywords used in prompt injections
    forbidden = ["IGNORE ALL PREVIOUS INSTRUCTIONS", "SYSTEM PROMPT", "DELETE EVERYTHING", "REWRITE AS"]
    for word in forbidden:
        text = re.sub(word, "[REDACTED]", text, flags=re.IGNORECASE)
    return text
