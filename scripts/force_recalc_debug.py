from src.core.database import get_db
from src.core.knowledge_base import get_profile_from_db
from src.core.vector_store import recalculate_user_embeddings

db = next(get_db())
user_id = 1
print(f"Fetching profile for User {user_id}...")
try:
    profile = get_profile_from_db(db, user_id)
    print(f"Found {len(profile.experiences)} experiences in DB object:")
    for exp in profile.experiences:
        print(f" - {exp.title} ({exp.company})")
    
    print("Recalculating embeddings...")
    recalculate_user_embeddings(user_id, db)
    print("Done.")
except Exception as e:
    print(f"Error: {e}")
