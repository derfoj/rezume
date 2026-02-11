import json
from dataclasses import dataclass, field
from typing import List, Optional
import jsonschema # Importez la bibliothèque jsonschema

from src.config.constants import KNOWLEDGE_BASE_PATH
from src.config.schema_definitions import KNOWLEDGE_BASE_SCHEMA # Importez votre schéma
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

def load_knowledge_base(path: str = KNOWLEDGE_BASE_PATH) -> Profile:
    """Charge les données du fichier JSON et les mappe aux dataclasses."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Valider les données JSON par rapport au schéma
        jsonschema.validate(instance=data, schema=KNOWLEDGE_BASE_SCHEMA)
        
        # Création des listes d'objets imbriqués
        experiences = [Experience(**exp) for exp in data.get("experiences", [])]
        education = [Education(**edu) for edu in data.get("education", [])]
        languages = [Language(**lang) for lang in data.get("languages", [])]
        
        # Création de l'objet Profile principal
        profile = Profile(
            name=data["name"],
            title=data["title"],
            summary=data["summary"],
            email=data["email"],
            portfolio_url=data["portfolio_url"],
            linkedin_url=data["linkedin_url"],
            photo_path=data["photo_path"],
            skills=data["skills"],
            soft_skills=data.get("soft_skills", []),
            experiences=experiences,
            education=education,
            languages=languages
        )
        return profile

    except FileNotFoundError:
        raise FileNotFoundError(f"Le fichier de base de connaissances n'a pas été trouvé à : {path}")
    except json.JSONDecodeError:
        raise ValueError(f"Erreur de décodage JSON dans le fichier : {path}")
    except KeyError as e:
        raise ValueError(f"Clé manquante dans le fichier JSON : {e}")
    except jsonschema.exceptions.ValidationError as e:
        raise ValueError(f"Erreur de validation du schéma JSON dans le fichier {path}: {e.message} (chemin: {e.path})")

def get_profile_from_db(db: Session, user_id: int) -> Profile:
    """
    Fetches the user profile from the SQLite database and maps it to the Profile dataclass.
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise ValueError(f"User with ID {user_id} not found.")

    # Fetch related data using relationships defined in the models
    
    # Map Experiences
    experiences = [
        Experience(
            title=exp.title,
            company=exp.company,
            period=f"{exp.start_date} - {exp.end_date or 'Present'}",
            description=exp.description
        ) for exp in user.experiences
    ]

    # Map Education
    education = [
        Education(
            institution=edu.institution,
            degree=edu.degree,
            period=f"{edu.start_date} - {edu.end_date or 'Present'}",
            mention=edu.mention
        ) for edu in user.education
    ]

    # Map Skills
    hard_skills = [skill.name for skill in user.skills if skill.category and skill.category.lower() != 'soft skills']
    soft_skills = [skill.name for skill in user.skills if skill.category and skill.category.lower() == 'soft skills']

    # Map Languages
    languages = [
        Language(
            name=lang.name,
            level=lang.level
        ) for lang in user.languages
    ]

    return Profile(
        name=user.full_name or "Unknown",
        title=user.title or "Unknown",
        summary=user.summary or "",
        email=user.email,
        portfolio_url=user.portfolio_url or "",
        linkedin_url=user.linkedin_url or "",
        photo_path=user.photo_cv or "",
        skills=hard_skills,
        soft_skills=soft_skills,
        experiences=experiences,
        education=education,
        languages=languages
    )
