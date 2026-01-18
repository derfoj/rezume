
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.database import Base
from src.models.user import User
from src.core.knowledge_base import get_profile_from_db

# Connect to REAL DB
SQLITE_URL = "sqlite:///./rezume.db"
engine = create_engine(SQLITE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def verify_migration():
    print("Verifying migration in rezume.db...")
    
    # Get migrated user (ID 2 assumed based on previous analysis)
    user = db.query(User).filter(User.id == 2).first()
    if not user:
        print("FAILURE: User ID 2 not found in DB!")
        return

    print(f"Found User: {user.email} (ID: {user.id})")
    
    try:
        profile = get_profile_from_db(db, user.id)
        
        print("\n--- Profile Data in DB ---")
        print(f"Name: {profile.name}")
        print(f"Title: {profile.title}")
        print(f"Skills: {len(profile.skills)} hard, {len(profile.soft_skills)} soft")
        print(f"Experiences: {len(profile.experiences)}")
        print(f"Education: {len(profile.education)}")
        
        if len(profile.experiences) > 0:
            print("\nLatest Experience:")
            print(f" - {profile.experiences[0].title} at {profile.experiences[0].company}")

        print("\nSUCCESS: Data is present in DB.")
        
    except Exception as e:
        print(f"\nFAILURE during profile fetch: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_migration()
