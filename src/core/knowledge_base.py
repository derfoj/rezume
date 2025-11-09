import json
from dataclasses import dataclass
from typing import List, Optional
from src.config.constants import KNOWLEDGE_BASE_PATH

@dataclass
class Experience:
    id: str
    title: str
    company: str
    start_date: str
    end_date: Optional[str]
    description: str

@dataclass
class Education:
    school: str
    degree: str
    start_date: str
    end_date: Optional[str]

@dataclass
class Profile:
    id: str
    name: str
    title: str
    summary: str
    skills: List[str]
    soft_skills: List[str]
    experiences: List[Experience]
    education: List[Education]

def load_knowledge_base(path: str = KNOWLEDGE_BASE_PATH) -> Profile:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return Profile(
        id=data["id"],
        name=data["name"],
        title=data["title"],
        summary=data["summary"],
        skills=data["skills"],
        soft_skills=data["soft_skills"],
        experiences=[Experience(**exp) for exp in data["experiences"]],
        education=[Education(**edu) for edu in data["education"]],
    )
