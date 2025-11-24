# reZume : Votre Assistant de Carrière IA

![reZume](https://raw.githubusercontent.com/username/repo/main/data/img/Firefly%2020240423102924.png) 


**reZume** est une application intelligente conçue pour automatiser et optimiser la création de CVs personnalisés. Fini le temps perdu à adapter manuellement votre CV pour chaque offre d'emploi. reZume analyse l'offre, la compare à votre profil complet, et génère un CV percutant en LaTeX, prêt à être envoyé.

---

## 🎯 Fonctionnalités Clés

- **Analyse Sémantique d'Offres d'Emploi** : Extrait automatiquement les compétences et missions clés d'une offre d'emploi grâce à un agent LLM.
- **Recherche Sémantique d'Expériences** : Utilise un moteur de recherche vectorielle (FAISS avec similarité cosinus) pour trouver les expériences les plus pertinentes dans votre profil.
- **Scoring de Compatibilité** : Calcule un score pour évaluer l'adéquation de votre profil avec l'offre.
- **Génération de CV en PDF** : Utilise un agent LLM pour rédiger le contenu de votre CV dans un format LaTeX professionnel, optimisé pour les systèmes de suivi des candidatures (ATS).
- **Interface Web Simple** : Une interface en React pour une expérience utilisateur fluide.

---

## 🛠️ Stack Technique

- **Backend** :
  - **Framework** : Python, FastAPI
  - **IA & NLP** : LangChain, OpenAI/Mistral/Google GenAI, Sentence-Transformers
  - **Recherche Vectorielle** : Faiss
  - **Génération PDF** : LaTeX
- **Frontend** :
  - **Framework** : React (avec Vite)
  - **Styling** : Tailwind CSS
- **Base de Données** : Fichiers plats (JSON) pour la base de connaissances et les embeddings.

---

## 📂 Structure du Projet

```
reZume/
├── api/                  # Logique des points d'entrée de l'API FastAPI
├── data/                 # Données utilisateur (base de connaissances, exemples)
│   ├── knowledge_base.json # Votre profil complet
│   └── embeddings/         # Index vectoriels FAISS
├── frontend/             # Application frontend en React
├── src/                  # Cœur de la logique backend
│   ├── agents/           # Agents IA (Parser, Generator)
│   ├── core/             # Logique métier principale (orchestration, vector store)
│   └── config/           # Fichiers de configuration (prompts, schémas)
├── outputs/              # CVs générés
└── presentation.txt      # Fichier de présentation du projet
```

---

## 🚀 Installation

1.  **Clonez le dépôt :**
    ```bash
    git clone https://github.com/derfoj/reZume.git
    cd reZume
    ```

2.  **Configurez le Backend :**
    - Assurez-vous d'avoir Python 3.9+ installé.
    - Créez un environnement virtuel et activez-le :
      ```bash
      python -m venv .rezume
      source .rezume/bin/activate  # Sur Windows: .rezume\Scripts\activate
      ```
    - Installez les dépendances Python :
      ```bash
      pip install -r requirements.txt
      ```
    - Créez un fichier `.env` à la racine du projet et ajoutez votre clé API pour le LLM :
      ```
      OPENAI_API_KEY="sk-..."
      ```

3.  **Configurez le Frontend :**
    - Assurez-vous d'avoir Node.js et npm installés.
    - Naviguez dans le dossier `frontend` et installez les dépendances :
      ```bash
      cd frontend
      npm install
      cd ..
      ```

---

## ✨ Utilisation

1.  **Remplissez votre profil :**
    - Ouvrez le fichier `data/knowledge_base.json` et remplissez-le avec vos informations personnelles, vos compétences, vos expériences, etc.

2.  **Lancez le Backend :**
    - À la racine du projet, lancez le serveur FastAPI :
      ```bash
      python api.py
      ```
    - Le serveur sera disponible à l'adresse `http://localhost:8000`.

3.  **Lancez le Frontend :**
    - Dans un autre terminal, naviguez dans le dossier `frontend` et lancez l'application React :
      ```bash
      cd frontend
      npm run dev
      ```
    - L'application sera accessible à l'adresse `http://localhost:5173` (ou une autre adresse indiquée par Vite).

4.  **Générez votre CV :**
    - Ouvrez l'application dans votre navigateur.
    - Copiez-collez une offre d'emploi dans la zone de texte.
    - Cliquez sur "Analyser" pour voir le score de compatibilité.
    - Sélectionnez les expériences à inclure.
    - Cliquez sur "Générer CV" pour télécharger votre CV personnalisé en PDF.

---

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.
```
