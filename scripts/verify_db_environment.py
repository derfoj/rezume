import os
import sqlite3
from src.core.database import get_db, SQLITE_URL
from src.models.profile import Experience

print(f"CWD: {os.getcwd()}")
print(f"SQLITE_URL in code: {SQLITE_URL}")

if os.path.exists("rezume.db"):
    stat = os.stat("rezume.db")
    print(f"rezume.db found. Size: {stat.st_size}. Mtime: {stat.st_mtime}")
else:
    print("rezume.db NOT found in CWD.")

# Manual SQLite connection
try:
    conn = sqlite3.connect("rezume.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, user_id FROM experiences WHERE user_id = 1")
    rows = cursor.fetchall()
    print(f"Raw SQLite (./rezume.db) found {len(rows)} exps for User 1:")
    for r in rows:
        print(f"  [ID: {r[0]}] {r[1]}")
    conn.close()
except Exception as e:
    print(f"Raw SQLite error: {e}")

# SQLAlchemy connection
print("\nSQLAlchemy Check:")
db = next(get_db())
exps = db.query(Experience).filter(Experience.user_id == 1).all()
print(f"SQLAlchemy found {len(exps)} exps for User 1:")
for exp in exps:
    print(f"  [ID: {exp.id}] {exp.title}")
