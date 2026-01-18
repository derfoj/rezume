
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.database import Base
from src.models.user import User
from src.core.security import get_password_hash

# Connect to DB
SQLITE_URL = "sqlite:///./rezume.db"
engine = create_engine(SQLITE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def reset_password():
    user_id = 2
    new_password = "password123"
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        print(f"User ID {user_id} not found.")
        return

    print(f"Resetting password for {user.email}...")
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    print("Password updated successfully.")

if __name__ == "__main__":
    reset_password()
