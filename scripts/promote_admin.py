import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.core.database import SessionLocal
from src.models.user import User

def promote_user(email: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"Error: User with email {email} not found.")
            return

        user.role = "admin"
        db.commit()
        print(f"Success: User {email} has been promoted to admin.")
    except Exception as e:
        db.rollback()
        print(f"Error promoting user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/promote_admin.py <email>")
    else:
        promote_user(sys.argv[1])
