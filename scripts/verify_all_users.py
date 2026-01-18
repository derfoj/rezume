import sqlite3
import os

print(f"CWD: {os.getcwd()}")
try:
    conn = sqlite3.connect("rezume.db")
    cursor = conn.cursor()
    
    print("\n--- Users ---")
    cursor.execute("SELECT id, email FROM users")
    users = cursor.fetchall()
    for u in users:
        print(f"User [{u[0]}]: {u[1]}")
        
        print(f"  Experiences for User {u[0]}:")
        cursor.execute(f"SELECT id, title FROM experiences WHERE user_id = {u[0]}")
        exps = cursor.fetchall()
        if not exps:
            print("    (None)")
        for e in exps:
             print(f"    [ID: {e[0]}] {e[1]}")

    conn.close()
except Exception as e:
    print(f"Error: {e}")
