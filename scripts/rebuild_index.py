from src.core.database import SessionLocal
from src.core.vector_store import recalculate_user_embeddings
import logging

logging.basicConfig(level=logging.INFO)

def rebuild():
    db = SessionLocal()
    user_id = 1 # Assuming User 1
    print(f"Rebuilding index for User {user_id}...")
    recalculate_user_embeddings(user_id, db)
    db.close()
    print("Done!")

if __name__ == "__main__":
    rebuild()
