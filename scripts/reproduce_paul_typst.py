import os
import sys
from pathlib import Path

# Ajout du root au path pour les imports
sys.path.append(str(Path(__file__).parent.parent))

import typst

def reproduce_cv_paul():
    print("--- Reproduction du CV de Paul en Typst ---")
    
    # Données extraites du fichier .tex
    user_profile = {
        "name": "PAUL MOUYEBISSI",
        "title": "ALTERNANCE DATA | IA & AUTOMATISATION | 3 SEMAINES EN ENTREPRISE",
        "email": "andylionel443@gmail.com",
        "phone": "",
        "linkedin": "www.linkedin.com/in/mouyebissi-paul-655122285",
        "portfolio": "https://paulmouyebissi-com-e638.vercel.app/",
        "summary": "",
        "photo_path": None,
        "experiences": [
            {
                "company": "AF-Advisory",
                "date": "septembre 2025 - Decembre 2025",
                "position": "Developpeur IA",
                "description": [
                    "Développé une solution IA de type assistant data permettant à des utilisateurs non-techniques d'extraire, analyser et visualiser des informations complexes à partir de données tabulaires (CSV / Excel), sans écrire de SQL.",
                    "Amélioration de l'accessibilité aux données et réduction du temps d'analyse grâce à l'interaction en langage naturel, la génération automatique de requêtes SQL, et l'explication intelligente des résultats."
                ]
            },
            {
                "company": "Projet personnel",
                "date": "Mars 2025 - Présent",
                "position": "Développement d'un Studio de Thèmes VS Code",
                "description": [
                    "Conçu une application web dédiée à la création de thèmes pour l'IDE, améliorant l'expérience développeur.",
                    "Optimiser l'édition des configurations graphiques, réduisant le temps de personnalisation de 30%."
                ]
            },
            {
                "company": "Projet Personnel",
                "date": "Avril 2025 - Présent",
                "position": "Segmentation clients & Prédiction",
                "description": [
                    "Segmenter plus de 3000 clients et prédire les ventes/prix immobiliers via KMeans, PCA, t-SNE, atteignant une précision de 87%."
                ]
            },
            {
                "company": "Restaurant Chips & Chicken",
                "date": "Jan. 2024 - Mar. 2024",
                "position": "Data Analyst",
                "description": [
                    "Analyse de Performance : Conçu un tableau de bord interactif sous Power BI réduisant de 25% le temps d'analyse manuelle.",
                    "Automatisé le nettoyage et le prétraitement de données clients et transactionnelles via SQL et Pandas."
                ]
            },
            {
                "company": "Wellpack | AI Clinic",
                "date": "Jan 2025 - Mars 2025",
                "position": "Developpeur IA",
                "description": [
                    "Génération automatisée de SMS marketing avec IA. Conçu et implémenté un compteur de caractères ainsi qu'un moteur de troncature dynamique.",
                    "Développé un workflow générant trois variantes de SMS par requête, facilitant l'analyse comparative via A/B testing."
                ]
            },
            {
                "company": "Centre Européen de Recherche Clinique",
                "date": "janvier 2026 - Avril 2026",
                "position": "Machine Learning Ingenieur",
                "description": [
                    "Regulatory AI Assistant (RAG-based NLP System) : Built an internal AI assistant for regulatory support in clinical trials.",
                    "Implemented document ingestion, cleaning, chunking, and embeddings."
                ]
            }
        ],
        "education": [
            {
                "institution": "Aivancity School of AI & Data Science",
                "date": "2023 - Présent",
                "degree": "Master Intelligence Artificielle et Science de Données"
            },
            {
                "institution": "Lycée Jean Hilaire (Gabon)",
                "date": "Juin 2022 - Présent",
                "degree": "Baccalaureat Scientifique (Mathématiques et Sciences Physiques)"
            }
        ],
        "skills": {
            "hard": "MySQL, Test Unitaire, SQLite, JAVASCRIPT, tool calling, Excel, HTML/CSS, CI/CD, DataBricks, Spark, Docker, AWS, API integration, SentenceTransformers, Render, Vercel",
            "soft": "Pensée critique, Esprit d'analyse et de synthèse, Attention aux détails, Communication efficace"
        },
        "languages": "Français (Natif), Anglais (C1)"
    }
    
    # On va lire le template existant
    template_path = "src/templates/modern.typ"
    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()

    # Construction de l'appel avec les données de Paul
    # On formate les listes et dictionnaires Typst
    
    def format_list(items):
        return "(" + ", ".join([f'"{i}"' for i in items]) + ")"

    exp_list = []
    for exp in user_profile["experiences"]:
        desc = format_list(exp["description"])
        exp_list.append(f'(company: "{exp["company"]}", date: "{exp["date"]}", position: "{exp["position"]}", description: {desc})')
    
    edu_list = []
    for edu in user_profile["education"]:
        edu_list.append(f'(institution: "{edu["institution"]}", date: "{edu["date"]}", degree: "{edu["degree"]}")')

    photo_val = "none" if user_profile["photo_path"] is None else f'"{user_profile["photo_path"]}"'

    args = f"""(
  name: "{user_profile["name"]}",
  title: "{user_profile["title"]}",
  email: "{user_profile["email"]}",
  linkedin: "{user_profile["linkedin"]}",
  portfolio: "{user_profile["portfolio"]}",
  photo_path: {photo_val},
  experiences: ({", ".join(exp_list)}),
  education: ({", ".join(edu_list)}),
  skills: (
    hard: "{user_profile["skills"]["hard"]}",
    soft: "{user_profile["skills"]["soft"]}",
  ),
  languages: "{user_profile["languages"]}"
)"""

    full_code = template_content + "\n\n#resume" + args
    
    temp_typ = "reproduce_paul.typ"
    output_pdf = "outputs/reproduce_paul_typst.pdf"
    
    with open(temp_typ, "w", encoding="utf-8") as f:
        f.write(full_code)
        
    try:
        pdf_bytes = typst.compile(temp_typ)
        with open(output_pdf, "wb") as f:
            f.write(pdf_bytes)
        print(f"✅ Reproduction réussie ! PDF généré : {output_pdf}")
    except Exception as e:
        print(f"❌ Erreur de rendu Typst : {e}")
    finally:
        if os.path.exists(temp_typ):
            os.remove(temp_typ)

if __name__ == "__main__":
    reproduce_cv_paul()
