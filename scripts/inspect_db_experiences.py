import sqlite3
import os

def inspect_db():
    db_path = 'rezume.db'
    if not os.path.exists(db_path):
        print(f"Erreur: Le fichier {db_path} n'existe pas.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Lister les tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Tables trouvées : {tables}")

    if 'experiences' in tables:
        print("\n--- Contenu de la table 'experiences' ---")
        cursor.execute("PRAGMA table_info(experiences);")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Colonnes : {columns}")

        cursor.execute("SELECT * FROM experiences;")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
    else:
        print("\nTable 'experiences' non trouvée.")

    conn.close()

if __name__ == "__main__":
    inspect_db()
