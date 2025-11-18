🧠 Projet : Agentic CV AI
🎯 Objectif du projet

Agentic CV AI est un système intelligent conçu pour automatiser la création et la personnalisation de CV à partir d’une offre d’emploi et d’une base de connaissances personnelle (expériences, compétences, projets, réalisations, etc.).
L’objectif est de permettre à un utilisateur de générer un CV parfaitement aligné avec une offre spécifique, en s’appuyant sur des agents d’intelligence artificielle autonomes et collaboratifs.

⚙️ Principe général

Le projet repose sur une architecture multi-agents orchestrée par un agent central (Orchestrator).
Chaque module est indépendant, spécialisé dans une étape précise du processus, et communique avec les autres via des appels structurés et traçables.
Le tout s’appuie sur LangChain/LangGraph, des modèles de langage (LLM) (OpenAI, DeepSeek, etc.), et une base de connaissances vectorielle.

🧩 Architecture des modules
1. clean_offer

Rôle : Nettoie et normalise le texte brut d’une offre d’emploi.

Fonctionnalités :

Supprime les caractères inutiles, les balises HTML et les doublons.

Segmente et reformate le texte pour faciliter l’analyse.

Uniformise la mise en forme et la structure du contenu.

2. read_offer

Rôle : Analyse l’offre nettoyée pour en extraire les compétences, missions, valeurs et mots-clés stratégiques.

Techniques utilisées :

Extraction d’informations avec LLM.

Structuration via Pydantic pour garantir la cohérence des données.

Utilisation de règles et pondérations pour hiérarchiser les compétences.

3. select_experience

Rôle : Sélectionne les expériences, compétences et projets les plus pertinents du CV par rapport à l’offre.

Méthodes :

Recherche sémantique dans une base vectorielle (embeddings).

Pondération automatique selon la pertinence contextuelle.

Génération d’un mapping entre les exigences de l’offre et le profil de l’utilisateur.

4. update_resume

Rôle : Génère la nouvelle version du CV adaptée à l’offre.

Fonctionnalités :

Reformulation des expériences selon le ton, les mots-clés et les valeurs de l’offre.

Mise à jour du résumé professionnel, des compétences, et du style rédactionnel.

Génération d’un CV final au format PDF, DOCX ou Markdown.

🤖 Agent Orchestrator (Agent Central)

Coordonne les interactions entre les modules.

Gère le contexte global, la traçabilité et la séquence logique du traitement.

Assure la communication avec les LLM providers via des wrappers comme langchain_openai, langchain_community, ou langgraph.

Peut être configuré pour exécuter les modules en pipeline linéaire ou en graphe d’agents interconnectés.

🧱 Structure du projet
cv_agent/
├── README.md
├── requirements.txt
├── main.py
├── src/
│   ├── agents/
│   │   ├── orchestrator_agent.py
│   │   ├── parser_agent.py
│   │   ├── matching_agent.py
│   │   ├── optimizer_agent.py
│   │   └── generator_agent.py
│   ├── core/
│   │   ├── knowledge_base.py
│   │   ├── database.py
│   │   ├── vector_store.py
│   │   └── utils.py
│   ├── interfaces/
│   │   ├── api.py
│   │   ├── ui.py
│   │   └── prompts/
│   └── config/
│       ├── settings.yaml
│       ├── constants.py
│       └── schema_definitions.py
├── data/
│   ├── knowledge_base.json
│   ├── embeddings/
│   └── sample_job_offers/
└── outputs/
    └── generated_cvs/

🧩 Technologies principales

LangChain / LangGraph : orchestration et gestion du raisonnement multi-agents.

Python (3.11+) : langage principal du backend.

Pydantic : validation des schémas de données.

OpenAI / DeepSeek / Ollama : fournisseurs de modèles LLM.

Chroma / FAISS / Pinecone : bases vectorielles pour la recherche sémantique.

FastAPI / Flask : exposition d’API.

Streamlit / Reflex : interfaces utilisateur simples et interactives.



🚀 Résultats attendus

Génération automatique d’un CV personnalisé à partir d’une offre donnée.

Alignement intelligent entre les exigences du poste et le profil utilisateur.

Gain de temps significatif dans la préparation de candidatures.

Base de projet réutilisable pour d’autres outils d’IA RH (lettres de motivation, matching emploi, scoring de candidatures, etc.).