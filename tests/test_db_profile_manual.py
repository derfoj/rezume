
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.database import Base
from src.models.user import User
from src.models.profile import Experience, Education, Skill
from src.core.knowledge_base import get_profile_from_db

# Setup in-memory DB
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def test_get_profile():
    print("Setting up test data...")
    # Create User
    user = User(
        email="test@example.com",
        hashed_password="fakehash",
        full_name="Jean Dupont",
        title="Software Engineer",
        avatar_image="path/to/img.png"
    )
    db.add(user)
    db.commit() # Commit to get ID
    db.refresh(user)
    
    # Create Experience
    exp1 = Experience(
        user_id=user.id,
        title="Dev",
        company="Tech Corp",
        start_date="2020-01",
        end_date="2022-01",
        description="Coding stuff."
    )
    db.add(exp1)

    # Create Education
    edu1 = Education(
        user_id=user.id,
        institution="University",
        degree="Master",
        start_date="2015",
        end_date="2020",
        description="Studied CS."
    )
    db.add(edu1)

    # Create Skills
    skill1 = Skill(user_id=user.id, name="Python", category="Hard Skills")
    skill2 = Skill(user_id=user.id, name="Teamwork", category="Soft Skills")
    db.add_all([skill1, skill2])
    
    db.commit()
    
    print("Fetching profile from DB...")
    try:
        profile = get_profile_from_db(db, user.id)
        
        print("\n--- Profile Data ---")
        print(f"Name: {profile.name}")
        print(f"Title: {profile.title}")
        print(f"Skills: {profile.skills}")
        print(f"Soft Skills: {profile.soft_skills}")
        print(f"Experiences: {len(profile.experiences)}")
        print(f"Education: {len(profile.education)}")
        
        assert profile.name == "Jean Dupont"
        assert "Python" in profile.skills
        assert "Teamwork" in profile.soft_skills
        assert len(profile.experiences) == 1
        assert len(profile.education) == 1
        print("\nSUCCESS: Profile fetched and mapped correctly.")
        
    except Exception as e:
        print(f"\nFAILURE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_get_profile()
