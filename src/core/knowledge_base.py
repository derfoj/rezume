import json
from dataclasses import dataclass, field
from typing import List, Optional
import jsonschema

from src.config.constants import KNOWLEDGE_BASE_PATH
from src.config.schema_definitions import KNOWLEDGE_BASE_SCHEMA
from sqlalchemy.orm import Session
from src.models.user import User as UserModel
from src.models.profile import Experience as ExperienceModel, Education as EducationModel, Skill as SkillModel, Language as LanguageModel

@dataclass
class Language:
    name: str
    level: str

@dataclass
class Experience:
    title: str
    company: str
    period: str
    description: str

@dataclass
class Education:
    institution: str
    degree: str
    period: str
    mention: Optional[str] = None

@dataclass
class Profile:
    name: str
    title: str
    summary: str
    email: str
    portfolio_url: str
    linkedin_url: str
    photo_path: str
    skills: List[str]
    soft_skills: List[str]
    experiences: List[Experience]
    education: List[Education]
    languages: List[Language]

def get_profile_from_db(db: Session, user_id: int) -> Profile:
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise ValueError(f"Utilisateur {user_id} introuvable.")

    experiences = [
        Experience(
            title=exp.title or "Sans titre",
            company=exp.company or "Inconnue",
            period=f"{exp.start_date or ''} - {exp.end_date or 'Présent'}",
            description=exp.description or ""
        ) for exp in user.experiences
    ]

    education = [
        Education(
            institution=edu.institution or "Inconnue",
            degree=edu.degree or "Diplôme",
            period=f"{edu.start_date or ''} - {edu.end_date or 'Présent'}",
            mention=edu.mention
        ) for edu in user.education
    ]

    # Sécurité sur les catégories de compétences
    hard_skills = []
    soft_skills = []
    for s in user.skills:
        cat = str(s.category).lower() if s.category else ""
        if "soft" in cat:
            soft_skills.append(s.name)
        else:
            hard_skills.append(s.name)

    return Profile(
        name=user.full_name or "Utilisateur",
        title=user.title or "Candidat",
        summary=user.summary or "",
        email=user.email,
        portfolio_url=user.portfolio_url or "",
        linkedin_url=user.linkedin_url or "",
        photo_path=user.photo_cv or "",
        skills=hard_skills,
        soft_skills=soft_skills,
        experiences=experiences,
        education=education,
        languages=[Language(name=l.name, level=l.level) for l in user.languages]
    )
