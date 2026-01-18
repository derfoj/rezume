import json
import re
import logging
import os
from src.core.utils import load_yaml
from src.core.llm_provider import get_llm

logger = logging.getLogger(__name__)

class CVParserAgent:
    def __init__(self, prompt_path: str = "src/config/prompts/cv_parser.yaml"):
        self.prompt_cfg = load_yaml(prompt_path)
        
        # --- SMART PROVIDER SELECTION ---
        # If Groq key is available, use it with Mixtral for super-fast parsing.
        # Otherwise, fallback to the project default (OpenAI usually).
        provider = None
        model = None
        
        if os.getenv("GROQ_API_KEY"):
            logger.info("Groq API Key detected. Using Groq/Llama 3 for CV Parsing (Fast & Efficient).")
            provider = "groq"
            model = "llama-3.3-70b-versatile"
        
        try:
            self.llm = get_llm(provider=provider, model=model)
            logger.info(f"CVParserAgent initialized with {provider or 'default'} / {model or 'default'}.")
        except Exception as e:
            self.llm = None
            logger.error(f"Failed to initialize LLM for CVParserAgent: {e}")

    def parse_cv(self, cv_text: str) -> dict:
        """
        Uses the LLM to parse raw CV text into structured JSON data.
        """
        if not self.llm:
            raise RuntimeError("LLM not available for CV parsing.")

        template = self.prompt_cfg["template"]
        prompt = template.replace("{{cv_text}}", cv_text)
        
        try:
            # We explicitly request JSON mode if supported (Groq supports it)
            # disabling json_mode=True to fix 400 Bad Request with Groq/Mixtral
            resp = self.llm.chat(prompt) 
            # Try to extract JSON from the response
            return self._extract_json(resp)
        except Exception as e:
            logger.error(f"Error during CV parsing: {e}")
            raise ValueError(f"Failed to parse CV content: {str(e)}")

    def _extract_json(self, text: str) -> dict:
        """Helper to extract and parse JSON block from LLM output."""
        try:
            # Try direct parse
            return json.loads(text.strip())
        except json.JSONDecodeError:
            # Look for markdown code blocks
            match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
            if not match:
                match = re.search(r"(\{.*?\})", text, re.DOTALL)
            
            if match:
                return json.loads(match.group(1))
            
            raise ValueError(f"No valid JSON found in LLM response. Raw text: {text[:100]}...")