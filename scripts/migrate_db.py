import sys
import os
from pathlib import Path
from sqlalchemy import text

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.core.database import engine

def migrate():
    print("Starting migration...")
    with engine.connect() as connection:
        try:
            # Check if role column exists (generic enough for both SQLite and Postgres)
            print("Adding 'role' column to 'users' table...")
            connection.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'user';"))
            connection.commit()
            print("Success: 'role' column added.")
        except Exception as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                print("Note: 'role' column already exists.")
            else:
                print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate()
