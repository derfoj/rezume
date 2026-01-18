from src.core.database import get_db
from src.core.knowledge_base import get_profile_from_db
from src.models.profile import Experience as ExpModel

db = next(get_db())
user_id = 1
print(f"DATABASE FILE: {db.bind.url.database}")

print(f"--- Raw Query Check for User {user_id} ---")
raw_exps = db.query(ExpModel).filter(ExpModel.user_id == user_id).all()
print(f"Found {len(raw_exps)} raw experiences.")
for exp in raw_exps:
    print(f"  [ID: {exp.id}] {exp.title}")

print("\n--- get_profile_from_db Check ---")
profile = get_profile_from_db(db, user_id)
print(f"Found {len(profile.experiences)} profile experiences.")
for i, exp in enumerate(profile.experiences):
    print(f"  [#{i}] {exp.title}")

