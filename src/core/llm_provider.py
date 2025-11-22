# src/core/llm_provider.py
"""
Wrapper LLM minimal et stable.
Actuellement supporté : OpenAI via package `openai` (nouveau SDK >=1.0).
Retourne un objet avec méthode `chat(prompt: str) -> str`.
"""

import os
from openai import OpenAI
from src.core.utils import load_yaml


def _make_openai_client(model_name: str, temperature: float, max_tokens: int):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY non défini dans les variables d'environnement.")

    # Création du client OpenAI
    client = OpenAI(api_key=api_key)

    class OpenAIWrapper:
        def __init__(self, model, temp, max_tokens):
            self.model = model
            self.temperature = temp
            self.max_tokens = max_tokens

        def chat(self, prompt: str, json_mode: bool = False) -> str:
            messages = [{"role": "user", "content": prompt}]
            
            request_params = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            }

            if json_mode:
                request_params["response_format"] = {"type": "json_object"}

            resp = client.chat.completions.create(**request_params)
            # Extraction sécurisée du contenu
            if not resp.choices or len(resp.choices) == 0:
                return ""
            return resp.choices[0].message.content or ""

    return OpenAIWrapper(model_name, temperature, max_tokens)


def get_llm():
    cfg = load_yaml("src/config/settings.yaml")
    provider = cfg.get("llm_provider", "openai")
    model_name = cfg.get("model_name", "gpt-4o-mini")
    temperature = float(cfg.get("temperature", 0.3))
    max_tokens = int(cfg.get("max_output_tokens", 800))

    if provider == "openai":
        return _make_openai_client(model_name, temperature, max_tokens)

    # Placeholders pour d'autres providers (Mistral, Gemini, Ollama)
    raise NotImplementedError(
        f"Provider '{provider}' non supporté par la version actuelle du wrapper. "
        "Ajoute une implémentation similaire si tu installes leur SDK."
    )
