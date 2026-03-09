from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel, ConfigDict
from src.core.database import get_db
from src.models.user import User
from src.models.profile import Experience, Skill, Education, Language
from src.core.security import verify_password
from src.api.auth import router as auth_router, get_current_user
from src.core.vector_store import recalculate_user_embeddings
import os
import shutil
import uuid

router = APIRouter()

# --- Schemas ---

class ExperienceBase(BaseModel):
    title: str
    company: str
    location: str | None = None
    description: str | None = None
    start_date: str | None = None
    end_date: str | None = None

class ExperienceCreate(ExperienceBase):
    pass

class ExperienceResponse(ExperienceBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class EducationBase(BaseModel):
    institution: str
    degree: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None
    mention: str | None = None

class EducationCreate(EducationBase):
    pass

class EducationResponse(EducationBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class SkillBase(BaseModel):
    name: str
    category: str | None = None

class SkillCreate(SkillBase):
    pass

class SkillResponse(SkillBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class LanguageBase(BaseModel):
    name: str
    level: str | None = None

class LanguageCreate(LanguageBase):
    pass

class LanguageResponse(LanguageBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class UserResponse(BaseModel):
    email: str
    full_name: str | None = None
    avatar_image: str | None = "default"
    photo_cv: str | None = None
    title: str | None = "Étudiant"
    summary: str | None = None
    portfolio_url: str | None = None
    language: str | None = "fr"
    theme: str | None = "light"
    selected_template: str | None = "classic"
    linkedin_url: str | None = None
    search_status: str | None = "listening"
    llm_provider: str | None = "openai"
    llm_model: str | None = "gpt-4o-mini"
    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    full_name: str | None = None
    title: str | None = None
    summary: str | None = None
    portfolio_url: str | None = None
    avatar_image: str | None = None
    language: str | None = None
    theme: str | None = None
    selected_template: str | None = None
    linkedin_url: str | None = None
    search_status: str | None = None
    llm_provider: str | None = None
    llm_model: str | None = None

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

# --- Endpoints ---

@router.get("/profile/me", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/profile/me", response_model=UserResponse)
def update_profile(
    user_update: UserUpdate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(current_user, key, value)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/profile/upload-photo")
async def upload_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Ensure directory exists
    upload_dir = "data/img/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    if file_extension.lower() not in [".jpg", ".jpeg", ".png"]:
        raise HTTPException(status_code=400, detail="Only JPG and PNG allowed")
        
    filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Update user in DB (store relative path)
    current_user.photo_cv = f"uploads/{filename}"
    db.add(current_user)
    db.commit()
    
    return {"photo_url": f"uploads/{filename}"}

@router.post("/profile/upload-avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Ensure directory exists
    upload_dir = "data/img/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    if file_extension.lower() not in [".jpg", ".jpeg", ".png"]:
        raise HTTPException(status_code=400, detail="Only JPG and PNG allowed")
        
    filename = f"avatar_{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Update user in DB (store relative path)
    current_user.avatar_image = f"uploads/{filename}"
    db.add(current_user)
    db.commit()
    
    return {"avatar_url": f"uploads/{filename}"}

@router.put("/profile/password")
def update_password(
    pass_update: PasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(pass_update.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    
    from src.core.security import get_password_hash
    current_user.hashed_password = get_password_hash(pass_update.new_password)
    db.add(current_user)
    db.commit()
    return {"message": "Password updated successfully"}

# --- Experiences ---
@router.get("/profile/experiences", response_model=List[ExperienceResponse])
def get_experiences(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Experience).filter(Experience.user_id == current_user.id).all()

@router.post("/profile/experiences", response_model=ExperienceResponse)
def create_experience(
    experience: ExperienceCreate, 
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    db_exp = Experience(**experience.model_dump(), user_id=current_user.id)
    db.add(db_exp)
    db.commit()
    db.refresh(db_exp)
    
    background_tasks.add_task(recalculate_user_embeddings, current_user.id, db)
    return db_exp

@router.put("/profile/experiences/{exp_id}", response_model=ExperienceResponse)
def update_experience(
    exp_id: int,
    experience: ExperienceCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_exp = db.query(Experience).filter(Experience.id == exp_id, Experience.user_id == current_user.id).first()
    if not db_exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    
    for key, value in experience.model_dump().items():
        setattr(db_exp, key, value)
    
    db.commit()
    db.refresh(db_exp)
    background_tasks.add_task(recalculate_user_embeddings, current_user.id, db)
    return db_exp

@router.delete("/profile/experiences/{exp_id}")
def delete_experience(
    exp_id: int, 
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    db_exp = db.query(Experience).filter(Experience.id == exp_id, Experience.user_id == current_user.id).first()
    if not db_exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    
    db.delete(db_exp)
    db.commit()
    background_tasks.add_task(recalculate_user_embeddings, current_user.id, db)
    return {"message": "Experience deleted"}

# --- Education ---
@router.get("/profile/education", response_model=List[EducationResponse])
def get_education(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Education).filter(Education.user_id == current_user.id).all()

@router.post("/profile/education", response_model=EducationResponse)
def create_education(
    education: EducationCreate, 
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    db_edu = Education(**education.model_dump(), user_id=current_user.id)
    db.add(db_edu)
    db.commit()
    db.refresh(db_edu)
    background_tasks.add_task(recalculate_user_embeddings, current_user.id, db)
    return db_edu

@router.put("/profile/education/{edu_id}", response_model=EducationResponse)
def update_education(
    edu_id: int,
    education: EducationCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_edu = db.query(Education).filter(Education.id == edu_id, Education.user_id == current_user.id).first()
    if not db_edu:
        raise HTTPException(status_code=404, detail="Education not found")

    for key, value in education.model_dump().items():
        setattr(db_edu, key, value)

    db.commit()
    db.refresh(db_edu)
    background_tasks.add_task(recalculate_user_embeddings, current_user.id, db)
    return db_edu

@router.delete("/profile/education/{edu_id}")
def delete_education(
    edu_id: int, 
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    db_edu = db.query(Education).filter(Education.id == edu_id, Education.user_id == current_user.id).first()
    if not db_edu:
        raise HTTPException(status_code=404, detail="Education not found")
    
    db.delete(db_edu)
    db.commit()
    background_tasks.add_task(recalculate_user_embeddings, current_user.id, db)
    return {"message": "Education deleted"}

# --- Skills ---
@router.get("/profile/skills", response_model=List[SkillResponse])
def get_skills(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Skill).filter(Skill.user_id == current_user.id).all()

@router.post("/profile/skills", response_model=SkillResponse)
def create_skill(
    skill: SkillCreate, 
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    db_skill = Skill(**skill.model_dump(), user_id=current_user.id)
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    background_tasks.add_task(recalculate_user_embeddings, current_user.id, db)
    return db_skill

@router.put("/profile/skills/{skill_id}", response_model=SkillResponse)
def update_skill(
    skill_id: int,
    skill: SkillCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_skill = db.query(Skill).filter(Skill.id == skill_id, Skill.user_id == current_user.id).first()
    if not db_skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    for key, value in skill.model_dump().items():
        setattr(db_skill, key, value)

    db.commit()
    db.refresh(db_skill)
    background_tasks.add_task(recalculate_user_embeddings, current_user.id, db)
    return db_skill

@router.delete("/profile/skills/{skill_id}")
def delete_skill(
    skill_id: int, 
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    db_skill = db.query(Skill).filter(Skill.id == skill_id, Skill.user_id == current_user.id).first()
    if not db_skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    db.delete(db_skill)
    db.commit()
    background_tasks.add_task(recalculate_user_embeddings, current_user.id, db)
    return {"message": "Skill deleted"}

# --- Languages ---
@router.get("/profile/languages", response_model=List[LanguageResponse])
def get_languages(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Language).filter(Language.user_id == current_user.id).all()

@router.post("/profile/languages", response_model=LanguageResponse)
def create_language(
    language: LanguageCreate, 
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    db_lang = Language(**language.model_dump(), user_id=current_user.id)
    db.add(db_lang)
    db.commit()
    db.refresh(db_lang)
    background_tasks.add_task(recalculate_user_embeddings, current_user.id, db)
    return db_lang

@router.put("/profile/languages/{lang_id}", response_model=LanguageResponse)
def update_language(
    lang_id: int,
    language: LanguageCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_lang = db.query(Language).filter(Language.id == lang_id, Language.user_id == current_user.id).first()
    if not db_lang:
        raise HTTPException(status_code=404, detail="Language not found")

    for key, value in language.model_dump().items():
        setattr(db_lang, key, value)

    db.commit()
    db.refresh(db_lang)
    background_tasks.add_task(recalculate_user_embeddings, current_user.id, db)
    return db_lang

@router.delete("/profile/languages/{lang_id}")
def delete_language(
    lang_id: int, 
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    db_lang = db.query(Language).filter(Language.id == lang_id, Language.user_id == current_user.id).first()
    if not db_lang:
        raise HTTPException(status_code=404, detail="Language not found")
    
    db.delete(db_lang)
    db.commit()
    background_tasks.add_task(recalculate_user_embeddings, current_user.id, db)
    return {"message": "Language deleted"}
