import sqlite3
import os

db_path = "rezume.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("SELECT id, email, full_name, avatar_image FROM users")
rows = c.fetchall()
print("ID | Email | Full Name | Avatar")
print("-" * 50)
for row in rows:
    print(row)
conn.close()
