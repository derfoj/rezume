from sqlalchemy import Column, Integer, String, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from src.core.database import Base

class Experience(Base):
    __tablename__ = "experiences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    title = Column(String, index=True)
    company = Column(String, nullable=True)
    location = Column(String, nullable=True)
    start_date = Column(String, nullable=True) 
    end_date = Column(String, nullable=True)
    description = Column(Text, nullable=True) # The full description text
    
    # Vector embedding for semantic search (stored as JSON/List check later if we use pgvector)
    # For SQLite/Prototype, we might store this separate or as a BLOB/JSON
    embedding = Column(JSON, nullable=True) 

    owner = relationship("src.models.user.User", backref="experiences")

class Education(Base):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    institution = Column(String)
    degree = Column(String, nullable=True)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    mention = Column(String, nullable=True)

    owner = relationship("src.models.user.User", backref="education")

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    name = Column(String, index=True)
    category = Column(String, nullable=True) # e.g., "Languages", "Frameworks"

    owner = relationship("src.models.user.User", backref="skills")

class Language(Base):
    __tablename__ = "languages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    name = Column(String, index=True)
    level = Column(String, nullable=True)

    owner = relationship("src.models.user.User", backref="languages")
