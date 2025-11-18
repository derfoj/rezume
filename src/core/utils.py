import os, json, yaml

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
