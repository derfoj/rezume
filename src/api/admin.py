from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.core.database import get_db
from src.api.auth import get_admin_user
from src.models.user import User
from src.models.profile import Experience, Skill
from src.models.usage import UsageLog

router = APIRouter()

@router.get("/stats")
def get_system_stats(admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    """
    Returns global statistics for the admin dashboard.
    """
    total_users = db.query(User).count()
    total_experiences = db.query(Experience).count()
    total_skills = db.query(Skill).count()
    
    # AI Stats from UsageLog
    gen_count = db.query(UsageLog).filter(UsageLog.action == 'cv_generation').count()
    analysis_count = db.query(UsageLog).filter(UsageLog.action == 'job_analysis').count()
    
    # Success Rate
    errors = db.query(UsageLog).filter(UsageLog.status == 'error').count()
    total_actions = db.query(UsageLog).count()
    success_rate = ((total_actions - errors) / total_actions * 100) if total_actions > 0 else 100

    # Recent Activity
    recent_logs = db.query(UsageLog).order_by(UsageLog.timestamp.desc()).limit(10).all()
    activity = [
        {
            "id": log.id,
            "action": log.action,
            "status": log.status,
            "timestamp": log.timestamp,
            "user_id": log.user_id
        } for log in recent_logs
    ]

    return {
        "overview": {
            "users": total_users,
            "experiences": total_experiences,
            "skills": total_skills,
            "cv_generated": gen_count,
            "analysis_performed": analysis_count
        },
        "performance": {
            "success_rate": round(success_rate, 2),
            "total_calls": total_actions
        },
        "recent_activity": activity
    }

@router.get("/users")
def list_all_users(admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    """Lists all users with their roles and signup dates."""
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "title": u.title
        } for u in users
    ]
