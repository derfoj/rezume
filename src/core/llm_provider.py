import os
from anthropic import Anthropic
from openai import OpenAI
from groq import Groq
from src.core.utils import load_yaml

# --- FACTORY FUNCTIONS ---

def _make_openai_client(model_name: str, temperature: float, max_tokens: int, api_key: str = None):
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        return None 
        
    client = OpenAI(api_key=key)

    class OpenAIWrapper:
        def chat(self, prompt: str, json_mode: bool = False) -> str:
            params = {
                "model": model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if json_mode:
                params["response_format"] = {"type": "json_object"}
            
            try:
                resp = client.chat.completions.create(**params)
                return resp.choices[0].message.content or ""
            except Exception as e:
                return f"Error (OpenAI): {str(e)}"

    return OpenAIWrapper()

def _make_groq_client(model_name: str, temperature: float, max_tokens: int, api_key: str = None):
    key = api_key or os.getenv("GROQ_API_KEY")
    if not key:
        return None 
        
    client = Groq(api_key=key)

    class GroqWrapper:
        def chat(self, prompt: str, json_mode: bool = False) -> str:
            # Groq supports JSON mode for some models (like llama-3.3-70b-versatile)
            # We set response_format if json_mode is requested
            params = {
                "model": model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if json_mode:
                params["response_format"] = {"type": "json_object"}
            
            try:
                resp = client.chat.completions.create(**params)
                return resp.choices[0].message.content or ""
            except Exception as e:
                return f"Error (Groq): {str(e)}"

    return GroqWrapper()

def _make_anthropic_client(model_name: str, temperature: float, max_tokens: int, api_key: str = None):
    key = api_key or os.getenv("ANTHROPIC_API_KEY")
    if not key:
         return None

    client = Anthropic(api_key=key)

    class AnthropicWrapper:
        def chat(self, prompt: str, json_mode: bool = False) -> str:
            try:
                message = client.messages.create(
                    model=model_name,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[{"role": "user", "content": prompt}]
                )
                return message.content[0].text
            except Exception as e:
                return f"Error (Anthropic): {str(e)}"

    return AnthropicWrapper()

def _make_gemini_client(model_name: str, temperature: float, max_tokens: int, api_key: str = None):
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        return None

    from google import genai
    client = genai.Client(api_key=key)

    class GeminiWrapper:
        def chat(self, prompt: str, json_mode: bool = False) -> str:
            try:
                config = {
                    "temperature": temperature,
                    "max_output_tokens": max_tokens
                }
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config
                )
                return response.text
            except Exception as e:
                 return f"Error (Gemini): {str(e)}"

    return GeminiWrapper()


def get_llm(provider: str = None, model: str = None, user_api_key: str = None):
    """
    Returns an LLM client based on arguments or default config.
    Prioritizes args > config.
    """
    cfg = load_yaml("src/config/settings.yaml")
    
    # Defaults from config
    target_provider = provider or cfg.get("llm_provider", "openai")
    target_model = model or cfg.get("model_name", "gpt-4o-mini")
    temperature = float(cfg.get("temperature", 0.3))
    max_tokens = int(cfg.get("max_output_tokens", 2048)) # Increased default for parsing

    if target_provider == "openai":
        return _make_openai_client(target_model, temperature, max_tokens, user_api_key)
    elif target_provider == "groq":
        return _make_groq_client(target_model, temperature, max_tokens, user_api_key)
    elif target_provider == "anthropic":
        return _make_anthropic_client(target_model, temperature, max_tokens, user_api_key)
    elif target_provider == "gemini":
        return _make_gemini_client(target_model, temperature, max_tokens, user_api_key)
    
    # Fallback
    return _make_openai_client("gpt-4o-mini", temperature, max_tokens, user_api_key)