from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from src.core.database import Base

class UsageLog(Base):
    """
    Table to track system usage: CV generations, analysis requests, etc.
    """
    __tablename__ = "usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String) # 'cv_generation', 'job_analysis', 'profile_import'
    provider = Column(String, nullable=True) # 'openai', 'groq', etc.
    model = Column(String, nullable=True)
    status = Column(String) # 'success', 'error'
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
