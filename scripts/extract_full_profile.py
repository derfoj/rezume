import sqlite3
import os

def extract_all_profile_data():
    db_path = 'rezume.db'
    if not os.path.exists(db_path):
        return "Erreur: Fichier base de données non trouvé."

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    output = []
    output.append("============================================================")
    output.append("RECAPITULATIF COMPLET DU PROFIL - REZUME DB")
    output.append("============================================================\n")

    # Get users
    cursor.execute("SELECT id, email, full_name FROM users;")
    users = cursor.fetchall()

    for user_id, email, name in users:
        output.append(f"👤 UTILISATEUR: {name or 'Inconnu'} ({email}) [ID: {user_id}]")
        output.append("-" * 60)

        # 1. Experiences
        output.append("\n--- EXPÉRIENCES PROFESSIONNELLES ---")
        cursor.execute("SELECT title, company, start_date, end_date, description FROM experiences WHERE user_id = ?;", (user_id,))
        exps = cursor.fetchall()
        for title, company, start, end, desc in exps:
            output.append(f"• {title} @ {company} ({start} - {end or 'Présent'})")
            if desc:
                # Indent description for better readability
                indented_desc = "\n      ".join(desc.split('\n'))
                output.append(f"  Détails: {indented_desc}")
        
        # 2. Education
        output.append("\n--- FORMATION & DIPLÔMES ---")
        cursor.execute("SELECT institution, degree, start_date, end_date, description FROM education WHERE user_id = ?;", (user_id,))
        edus = cursor.fetchall()
        for inst, degree, start, end, desc in edus:
            output.append(f"• {degree} - {inst} ({start} - {end or 'Présent'})")
            if desc: output.append(f"  Détails: {desc}")

        # 3. Skills
        output.append("\n--- COMPÉTENCES (SKILLS) ---")
        cursor.execute("SELECT name, category FROM skills WHERE user_id = ?;", (user_id,))
        skills = cursor.fetchall()
        # Group by category
        categories = {}
        for name, cat in skills:
            cat = cat or "Général"
            if cat not in categories: categories[cat] = []
            categories[cat].append(name)
        
        for cat, items in categories.items():
            output.append(f"  [{cat}]: {', '.join(items)}")

        # 4. Languages
        output.append("\n--- LANGUES ---")
        cursor.execute("SELECT name, level FROM languages WHERE user_id = ?;", (user_id,))
        langs = cursor.fetchall()
        for name, level in langs:
            output.append(f"• {name} ({level or 'Non spécifié'})")

        output.append("\n" + "="*60 + "\n")

    conn.close()
    return "\n".join(output)

if __name__ == "__main__":
    full_recap = extract_all_profile_data()
    with open('data/recap_complet_profil.txt', 'w', encoding='utf-8') as f:
        f.write(full_recap)
    print("Fichier data/recap_complet_profil.txt généré avec succès.")
