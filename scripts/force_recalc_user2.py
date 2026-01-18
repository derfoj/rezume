from src.core.database import get_db
from src.core.vector_store import recalculate_user_embeddings

db = next(get_db())
# Forced recalculation for User 2
print("Recalculating embeddings for User 2 (Paul)...")
try:
    recalculate_user_embeddings(2, db)
    print("Success!")
except Exception as e:
    print(f"Error: {e}")
