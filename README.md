# reZume : Votre Assistant de Carrière IA

![reZume](data/img/reZume_logo.png) 

**reZume** est une application full-stack intelligente conçue pour automatiser et optimiser la création de CVs personnalisés. Fini le temps perdu à adapter manuellement votre CV pour chaque offre d'emploi. reZume analyse l'offre, la compare à votre profil complet, et génère un CV percutant en LaTeX, prêt à être envoyé.

---

## 🎯 Fonctionnalités Clés

- **Import Intelligent de CV** : Utilise **LlamaParse** (OCR avancé) et **LlamaIndex** pour extraire et structurer automatiquement vos expériences depuis un PDF existant.
- **Analyse Sémantique d'Offres** : Extrait les compétences et missions clés d'une offre d'emploi grâce à un pipeline IA robuste (Extraction Structurée).
- **Optimisation STAR** : Un agent IA dédié reformule vos descriptions d'expérience selon la méthode STAR (Situation, Tâche, Action, Résultat) pour un impact maximal.
- **Recherche Sémantique (RAG)** : Utilise un moteur de recherche vectorielle (FAISS) pour sélectionner les expériences les plus pertinentes de votre profil pour une offre donnée.
- **Génération de CV PDF** : Compile un CV professionnel en LaTeX/PDF, optimisé pour les ATS (Applicant Tracking Systems).
- **Prévisualisation Live** : Visualisez votre CV généré directement dans le navigateur avant de le télécharger.
- **Galerie de Templates** : Choisissez parmi plusieurs designs (Classique, Moderne) via une interface visuelle.

---

## 🛠️ Stack Technique

- **Backend** :
  - **Framework** : Python, FastAPI
  - **IA & NLP** : 
    - **LlamaIndex** & **LangChain** (Orchestration)
    - **Groq** (Inférence ultra-rapide avec Llama 3)
    - **LlamaParse** (Parsing de documents complexes)
    - **Sentence-Transformers** (Embeddings)
  - **Base de Données** : SQLite (via SQLAlchemy)
  - **Recherche Vectorielle** : FAISS
  - **Génération PDF** : LaTeX (MiKTeX/TeX Live requis)

- **Frontend** :
  - **Framework** : React (Vite)
  - **Styling** : Tailwind CSS + Tailwind Animate
  - **État** : Context API

---

## 📂 Structure du Projet

```
reZume/
├── api.py                # Point d'entrée du serveur FastAPI
├── frontend/             # Application React
├── src/                  # Cœur de la logique backend
│   ├── agents/           # Agents IA (Extractor, Optimizer, Parser, Generator)
│   ├── api/              # Routes API (Auth, Profile, Analysis, Generation)
│   ├── core/             # Logique métier (Database, Vector Store, PDF Extractor)
│   ├── models/           # Modèles de base de données (SQLAlchemy)
│   └── templates/        # Modèles LaTeX (.tex)
├── data/                 # Stockage local (Embeddings FAISS, Images)
└── requirements.txt      # Dépendances Python
```

---

## 🚀 Installation

1.  **Clonez le dépôt :**
    ```bash
    git clone https://github.com/derfoj/reZume.git
    cd reZume
    ```

2.  **Configurez le Backend :**
    - Assurez-vous d'avoir Python 3.10+ installé.
    - Créez un environnement virtuel et activez-le :
      ```bash
      python -m venv .rezume
      source .rezume/bin/activate  # Sur Windows: .rezume\Scripts\activate
      ```
    - Installez les dépendances Python :
      ```bash
      pip install -r requirements.txt
      ```
    - **Configuration des clés API (.env)** :
      Créez un fichier `.env` à la racine et ajoutez vos clés (Groq recommandé pour la vitesse) :
      ```env
      # Obligatoire pour l'intelligence
      GROQ_API_KEY="gsk_..."
      # Optionnel (pour le parsing PDF avancé)
      LLAMA_CLOUD_API_KEY="llx-..."
      # Optionnel (si vous n'utilisez pas Groq)
      OPENAI_API_KEY="sk-..."
      ```

3.  **Configurez le Frontend :**
    - Assurez-vous d'avoir Node.js installé.
    - Naviguez dans le dossier `frontend` et installez les dépendances :
      ```bash
      cd frontend
      npm install
      ```

---

## ✨ Utilisation

1.  **Lancez le Backend :**
    ```bash
    # À la racine du projet (environnement activé)
    python api.py
    ```
    Le serveur écoutera sur `http://localhost:8000`.

2.  **Lancez le Frontend :**
    ```bash
    # Dans le dossier frontend
    npm run dev
    ```
    L'application sera accessible sur `http://localhost:5173`.

3.  **Flux de Travail :**
    - **Créer un compte** : Inscrivez-vous sur la plateforme.
    - **Profil** : Importez votre CV (PDF). L'IA extraira vos données. Vérifiez et optimisez vos descriptions avec le bouton "Améliorer IA".
    - **Explorer** : Choisissez un template dans la galerie.
    - **CV Builder** : Collez une offre d'emploi. L'IA analyse le match, sélectionne vos meilleures expériences, et génère un aperçu PDF.
    - **Télécharger** : Récupérez votre CV optimisé.

---

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.