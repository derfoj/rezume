from src.core.database import get_db
from src.models.profile import Experience
from src.models.user import User

db = next(get_db())
users = db.query(User).all()

for user in users:
    print(f"--- User {user.id}: {user.email} ---")
    exps = db.query(Experience).filter(Experience.user_id == user.id).all()
    if not exps:
        print("  No experiences found.")
    for exp in exps:
        print(f"  [ID: {exp.id}] {exp.title} @ {exp.company}")
print("-" * 30)
