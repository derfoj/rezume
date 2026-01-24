from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
from src.core.database import get_db
from src.models.user import User
from src.models.profile import Experience, Skill, Education, Language
from src.core.security import verify_password
from src.api.auth import router as auth_router
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from src.core.security import SECRET_KEY, ALGORITHM
from fastapi import BackgroundTasks
from src.core.vector_store import recalculate_user_embeddings
from src.core.pdf_extractor import extract_text_from_pdf
# from src.agents.cv_parser import CVParserAgent # Deprecated
from src.agents.llama_extractor import LlamaExtractorAgent
import os
import shutil
import tempfile
import filetype # NEW
from pathlib import Path

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

MAX_FILE_SIZE = 5 * 1024 * 1024 # 5 MB

from fastapi import Request
import logging

logger = logging.getLogger(__name__)

def get_current_user(request: Request, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # DEBUG LOGGING
    logger.info(f"DEBUG: Cookies received: {request.cookies}")
    logger.info(f"DEBUG: Auth Header: {request.headers.get('Authorization')}")
    
    token = request.cookies.get("access_token")
    if not token:
        # Fallback to Authorization header for flexibility
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        else:
            logger.warning("DEBUG: No token found in cookies or header.")
            raise credentials_exception

    # Remove "Bearer " prefix if present in cookie (auth.py adds it)
    if token.startswith("Bearer "):
        token = token.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            logger.warning("DEBUG: Token payload missing email.")
            raise credentials_exception
    except JWTError as e:
        logger.warning(f"DEBUG: JWT Decode Error: {e}")
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        logger.warning(f"DEBUG: User not found in DB for email {email}")
        raise credentials_exception
    return user

# --- Pydantic Models for Response/Request ---
class ExperienceBase(BaseModel):
    title: str
    company: str | None = None
    location: str | None = None
    description: str | None = None
    start_date: str | None = None
    end_date: str | None = None

class ExperienceCreate(ExperienceBase):
    pass

class ExperienceResponse(ExperienceBase):
    id: int
    class Config:
        from_attributes = True

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
    class Config:
        from_attributes = True

class SkillBase(BaseModel):
    name: str
    category: str | None = None

class SkillCreate(SkillBase):
    pass

class SkillResponse(SkillBase):
    id: int
    class Config:
        from_attributes = True

class LanguageBase(BaseModel):
    name: str
    level: str | None = None

class LanguageCreate(LanguageBase):
    pass

class LanguageResponse(LanguageBase):
    id: int
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    email: str
    full_name: str | None = None
    avatar_image: str | None = "default"
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
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: str | None = None
    avatar_image: str | None = None
    title: str | None = None
    summary: str | None = None
    portfolio_url: str | None = None
    language: str | None = None
    theme: str | None = None
    selected_template: str | None = None
    linkedin_url: str | None = None
    openai_api_key: str | None = None
    search_status: str | None = None
    llm_provider: str | None = None
    llm_model: str | None = None

# --- CV Upload & Parsing ---

@router.post("/profile/upload-cv")
async def upload_cv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Uploads a PDF CV, parses it using AI, and returns the structured data 
    for user review (without saving to DB).
    """
    # 1. Basic Extension Check
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported (extension check).")

    temp_path = None
    try:
        # 2. Save uploaded file to temp (streaming to avoid memory overflow)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            size = 0
            while chunk := await file.read(1024 * 1024): # Read in 1MB chunks
                size += len(chunk)
                if size > MAX_FILE_SIZE:
                    tmp.close()
                    os.remove(tmp.name)
                    raise HTTPException(status_code=413, detail=f"File too large. Max size is {MAX_FILE_SIZE/1024/1024}MB.")
                tmp.write(chunk)
            temp_path = tmp.name

        # 3. Magic Number Check (Content-Type Verification)
        kind = filetype.guess(temp_path)
        if kind is None or kind.mime != "application/pdf":
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload a valid PDF.")

        # 4. Extract text
        text = extract_text_from_pdf(temp_path)
        if not text:
            raise ValueError("Could not extract text from the provided PDF.")

        # 5. Parse with AI using LlamaExtractorAgent
        extractor = LlamaExtractorAgent()
        data = extractor.extract_data(text)

        # 6. Return data to frontend for review
        return {
            "message": "CV parsed successfully",
            "data": data
        }

    except Exception as e:
        print(f"Error during CV parsing: {e}") 
        raise HTTPException(status_code=500, detail=f"Failed to parse CV: {str(e)}")
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

# --- Profile Photo Upload ---
@router.post("/profile/upload-photo")
async def upload_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Uploads a profile picture for the user.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    # Create uploads directory if not exists
    upload_dir = Path("data/img/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Filename: user_{id}_{filename} to avoid collisions but keep extension
    filename = f"user_{current_user.id}_{file.filename}"
    file_path = upload_dir / filename

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Update user profile
        # We store the relative path or a special marker to indicate it's an upload
        # Let's store: "uploads/filename"
        relative_path = f"uploads/{filename}"
        current_user.avatar_image = relative_path
        db.commit()
        
        return {"message": "Photo uploaded successfully", "path": relative_path}
    except Exception as e:
        print(f"Error uploading photo: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload photo.")

# --- Endpoints ---

@router.get("/profile/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/profile/me", response_model=UserResponse)
def update_me(
    user_update: UserUpdate, 
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.avatar_image is not None:
        current_user.avatar_image = user_update.avatar_image
    if user_update.title is not None:
        current_user.title = user_update.title
    if user_update.summary is not None:
        current_user.summary = user_update.summary
    if user_update.portfolio_url is not None:
        current_user.portfolio_url = user_update.portfolio_url
    if user_update.language is not None:
        current_user.language = user_update.language
    if user_update.theme is not None:
        current_user.theme = user_update.theme
    if user_update.selected_template is not None:
        current_user.selected_template = user_update.selected_template
    if user_update.linkedin_url is not None:
        current_user.linkedin_url = user_update.linkedin_url
    if user_update.openai_api_key is not None:
        current_user.openai_api_key = user_update.openai_api_key
    if user_update.search_status is not None:
        current_user.search_status = user_update.search_status
    if user_update.llm_provider is not None:
        current_user.llm_provider = user_update.llm_provider
    if user_update.llm_model is not None:
        current_user.llm_model = user_update.llm_model
    
    db.commit()
    db.refresh(current_user)
    
    # Trigger embedding recalculation
    background_tasks.add_task(recalculate_user_embeddings, current_user.id, db)
    
    return current_user

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
    db_exp = Experience(**experience.dict(), user_id=current_user.id)
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
    
    for key, value in experience.dict().items():
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
    db_edu = Education(**education.dict(), user_id=current_user.id)
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

    for key, value in education.dict().items():
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
    db_skill = Skill(**skill.dict(), user_id=current_user.id)
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

    for key, value in skill.dict().items():
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
    db_lang = Language(**language.dict(), user_id=current_user.id)
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

    for key, value in language.dict().items():
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