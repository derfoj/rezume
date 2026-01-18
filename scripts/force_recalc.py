from src.core.database import get_db
from src.core.vector_store import recalculate_user_embeddings
from src.models.user import User

db = next(get_db())
# Forced recalculation for User 1
print("Recalculating embeddings for User 1...")
try:
    recalculate_user_embeddings(1, db)
    print("Success!")
except Exception as e:
    print(f"Error: {e}")
