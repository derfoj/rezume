# src/models/schemas.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class Offer(BaseModel):
    id: Optional[str]
    raw_text: str
    cleaned_text: Optional[str] = None
    parsed: Optional[Dict[str, Any]] = None

class Experience(BaseModel):
    id: Optional[str]
    title: Optional[str]
    company: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    description: Optional[str]

class KnowledgeBase(BaseModel):
    id: str
    name: str
    title: Optional[str]
    skills: List[str] = []
    experiences: List[Experience] = []
