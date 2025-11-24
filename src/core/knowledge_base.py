import json
from dataclasses import dataclass, field
from typing import List, Optional
import jsonschema # Importez la bibliothèque jsonschema

from src.config.constants import KNOWLEDGE_BASE_PATH
from src.config.schema_definitions import KNOWLEDGE_BASE_SCHEMA # Importez votre schéma

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
