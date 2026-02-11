from sqlalchemy import Column, Integer, String, Text
from src.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, nullable=True)
    avatar_image = Column(String, default="default")
    photo_cv = Column(String, nullable=True) # Separate uploaded photo for CV
    title = Column(String, nullable=True, default="Étudiant")
    summary = Column(Text, nullable=True)
    portfolio_url = Column(String, nullable=True)
    language = Column(String, default="fr") # 'fr' or 'en'
    theme = Column(String, default="light") # 'light' or 'dark'
    selected_template = Column(String, default="modern") # 'modern' or 'photo_header'
    linkedin_url = Column(String, nullable=True)
    openai_api_key = Column(String, nullable=True)
    search_status = Column(String, default="listening") # listening, active, closed
    llm_provider = Column(String, default="openai") # openai, anthropic, gemini
    llm_model = Column(String, default="gpt-4o-mini")
    
    # We will add relationships later when profile.py is ready
    # experiences = relationship("Experience", back_populates="owner")
