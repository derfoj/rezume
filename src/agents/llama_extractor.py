from typing import List, Optional
from pydantic import BaseModel, Field
import os
import logging
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.core.llms import LLM
from src.core.llm_provider import get_llm

logger = logging.getLogger(__name__)

# --- Definition of Pydantic Models for Extraction ---
# These models mirror the ones in src/api/profile.py but are optimized for LLM extraction
# (e.g., with descriptions in Field to guide the LLM).

class ExperienceExtraction(BaseModel):
    title: str = Field(description="Job title")
    company: Optional[str] = Field(description="Company name. Leave empty if personal project or freelance.")
    location: Optional[str] = Field(description="City/Country of the job. Leave empty if remote or not found.")
    start_date: Optional[str] = Field(description="Start date (e.g., 'Jan 2020' or '2020'). Leave empty if not found.")
    end_date: Optional[str] = Field(description="End date (e.g., 'Dec 2022' or 'Present'). Leave empty if not found.")
    description: Optional[str] = Field(description="Detailed description of responsibilities and achievements. Leave empty if none provided.")

class EducationExtraction(BaseModel):
    institution: str = Field(description="Name of the university or school")
    degree: Optional[str] = Field(description="Degree obtained (e.g., 'Master in Computer Science'). Leave empty if not specified.")
    start_date: Optional[str] = Field(description="Start date")
    end_date: Optional[str] = Field(description="End date")
    mention: Optional[str] = Field(description="Honors or mention (e.g., 'Cum Laude')")
    description: Optional[str] = Field(description="Additional details about the program")

class LanguageExtraction(BaseModel):
    name: str = Field(description="Language name (e.g., 'English', 'French')")
    level: Optional[str] = Field(description="Proficiency level (e.g., 'Native', 'Fluent', 'B2'). Leave empty if not found.")

class CVData(BaseModel):
    full_name: str = Field(description="Full name of the candidate")
    title: Optional[str] = Field(description="Current professional title")
    summary: Optional[str] = Field(description="Short professional summary or profile description")
    linkedin_url: Optional[str] = Field(description="LinkedIn profile URL")
    portfolio_url: Optional[str] = Field(description="Portfolio or personal website URL")
    experiences: List[ExperienceExtraction] = Field(description="List of professional experiences")
    education: List[EducationExtraction] = Field(description="List of educational background")
    skills: List[str] = Field(description="List of hard/technical skills")
    soft_skills: List[str] = Field(description="List of soft/interpersonal skills")
    languages: List[LanguageExtraction] = Field(description="List of languages spoken")

class LlamaExtractorAgent:
    def __init__(self):
        # reuse the project's LLM provider logic, but we might need to adapt it
        # to LlamaIndex's LLM interface if it's not directly compatible.
        # For now, let's assume we can use LlamaIndex's OpenAI or Groq integrations directly
        # based on env vars, or wrap our get_llm if possible.
        # Simplest approach: Use LlamaIndex's built-in support for OpenAI/Groq/Mistral
        
        self.llm = self._get_llama_index_llm()
        
        # Define the extraction program
        prompt_template_str = """
        You are an expert CV parser. Extract the following information from the CV text provided below.
        Ensure that the output is a valid JSON object matching the specified schema.
        
        CV TEXT:
        {text}
        """
        
        self.program = LLMTextCompletionProgram.from_defaults(
            output_cls=CVData,
            prompt_template_str=prompt_template_str,
            llm=self.llm,
            verbose=True
        )

    def _get_llama_index_llm(self) -> LLM:
        """
        Returns a LlamaIndex compatible LLM instance based on environment configuration.
        """
        # We need to import the specific LLM classes from llama-index integrations
        # Since we just installed llama-index-core, we might need specific provider packages
        # like llama-index-llms-openai or llama-index-llms-groq.
        # If they are not installed, we might fallback or need to install them.
        
        # Let's check what's available or default to OpenAI (assuming standard setup)
        # Note: In a real 'pip install llama-index' scenario, OpenAI is usually included or separated.
        # We installed `llama-index-core`. We might need `pip install llama-index-llms-openai`.
        
        # For now, let's try to dynamic import.
        
        provider = os.getenv("LLM_PROVIDER", "openai").lower()
        api_key = os.getenv("OPENAI_API_KEY")
        
        try:
            if os.getenv("GROQ_API_KEY"):
                # Groq is often preferred for speed/parsing if available
                from llama_index.llms.groq import Groq
                return Groq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
            
            if provider == "openai" or not provider:
                from llama_index.llms.openai import OpenAI
                return OpenAI(model="gpt-4o-mini", api_key=api_key)
                
            # Fallback to OpenAI if others fail or not found
            from llama_index.llms.openai import OpenAI
            return OpenAI(model="gpt-4o-mini", api_key=api_key)

        except ImportError as e:
            logger.warning(f"Could not import specific LlamaIndex LLM provider: {e}. Falling back to default OpenAI.")
            # This might fail if llama-index-llms-openai is not installed.
            # We will handle this dependency check in the next step.
            raise e

    def extract_data(self, text: str) -> dict:
        """
        Extracts structured data from the given text using the defined schema.
        """
        try:
            output: CVData = self.program(text=text)
            return output.dict()
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            raise ValueError(f"Failed to extract structured data: {str(e)}")
