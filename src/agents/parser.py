import json
import re
import logging
import os
from typing import List, Optional
from pydantic.v1 import BaseModel, Field
from src.core.utils import load_yaml
from src.core.llm_provider import get_llm

# LlamaIndex imports
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.llms.openai import OpenAI
from llama_index.llms.groq import Groq

# Configure a logger for this module
logger = logging.getLogger(__name__)

class JobOfferData(BaseModel):
    class Config:
        arbitrary_types_allowed = True
    
    skills: List[str] = Field(description="List of required technical and soft skills")
    missions: List[str] = Field(description="Main responsibilities and tasks mentioned in the offer")
    values: List[str] = Field(description="Company values or culture mentioned in the offer")
    location: Optional[str] = Field(description="Job location if specified")
    contract_type: Optional[str] = Field(description="Type of contract (CDI, Stage, Alternance, etc.)")

class ParserAgent:
    def __init__(self, prompt_path: str = None):
        # We define the structured extraction program
        self.llm = self._get_llama_index_llm()
        
        # Load prompt from YAML if path provided
        prompt_template_str = None
        if prompt_path:
            try:
                config = load_yaml(prompt_path)
                prompt_template_str = config.get('template')
            except Exception as e:
                logger.warning(f"Failed to load prompt from {prompt_path}: {e}")

        # Fallback if YAML load failed or key missing
        if not prompt_template_str:
            prompt_template_str = """
            You are an expert recruitment analyst. Extract structured information from the following job offer text.
            Ensure the output strictly follows the schema.
            
            OFFER TEXT:
            {offer_text}
            """
        
        self.program = LLMTextCompletionProgram.from_defaults(
            output_cls=JobOfferData,
            prompt_template_str=prompt_template_str,
            llm=self.llm,
            verbose=True
        )

    def _get_llama_index_llm(self):
        # Reuse same logic as LlamaExtractorAgent
        provider = os.getenv("LLM_PROVIDER", "openai").lower()
        if os.getenv("GROQ_API_KEY"):
            return Groq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
        return OpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

    def _rule_based_extract(self, text: str):
        """A simple fallback extraction method based on keywords."""
        logger.info("Executing rule-based extraction as a fallback.")
        text_lower = text.lower()
        techs = ["python", "sql", "pandas", "scikit-learn", "machine learning", "flask", "docker", "power bi", "tableau"]
        skills = [s for s in techs if s in text_lower]
        missions = re.findall(r"(analyser|nettoyer|créer|développer|implémenter|déployer)[^\.]*", text_lower)
        return {"skills": skills, "missions": missions, "values": [], "location": None, "contract_type": None}

    def extract_information(self, offer_text: str):
        """
        Extracts structured information from job offer text using LlamaIndex Structured Extraction.
        """
        try:
            logger.info("Starting structured extraction for job offer.")
            output: JobOfferData = self.program(offer_text=offer_text)
            return output.model_dump()
        except Exception as e:
            logger.error(f"Structured extraction failed: {e}. Falling back to rule-based method.")
            return self._rule_based_extract(offer_text)
