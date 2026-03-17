
import os
import sys
import logging
from pathlib import Path

# Configuration du logging pour voir les tentatives
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ajout du dossier racine au sys.path
sys.path.append(os.getcwd())

from src.api.generation import background_generate_cv
from src.core.api_models import CVGenerationRequest
from src.models.usage import UsageLog
from src.models.user import User
from src.core.database import SessionLocal, engine, Base

def test_retry_loop():
    print("🚀 Démarrage du test de la boucle de retry (Contrainte 1 page)...")
    
    db = SessionLocal()
    try:
        # 1. S'assurer qu'un utilisateur de test existe (ID 1)
        user = db.query(User).filter(User.id == 1).first()
        if not user:
            print("❌ Utilisateur ID 1 non trouvé. Veuillez lancer le serveur ou créer un utilisateur d'abord.")
            return

        # 2. Créer un profil EXTRÊMEMENT long (25 expériences très détaillées)
        long_experiences = []
        for i in range(1, 26):
            long_experiences.append({
                "title": f"Poste de Direction Senior Très Long Numéro {i}",
                "company": f"Grande Entreprise Internationale de Prestige {i}",
                "period": "2010 - 2022",
                "location": "Paris, France",
                "description": (
                    "Responsable de la stratégie globale et de la transformation digitale à très grande échelle. "
                    "Management direct d'une équipe de 100 personnes à travers 5 continents. "
                    "Optimisation des processus métier complexes utilisant le Lean Six Sigma. "
                    "Augmentation du chiffre d'affaires de 50% sur trois ans grâce à l'innovation. "
                    "Mise en place de solutions d'IA complexes (Transformers, LLMs) et gestion de budgets de 50 millions d'euros. "
                    "Collaboration quotidienne avec les parties prenantes au niveau C-level. "
                    "Développement de partenariats stratégiques avec Google, Microsoft et Amazon. "
                    "Supervision du recrutement de 200 ingénieurs."
                )
            })

        # 3. Créer une entrée de log pour le job
        log_entry = UsageLog(
            user_id=user.id,
            action="cv_generation_test_retry",
            status="processing"
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        
        job_id = str(log_entry.id)
        print(f"📝 Job créé avec l'ID: {job_id}")

        # 4. Lancer la génération (qui devrait échouer au 1er coup et retry)
        request = CVGenerationRequest(
            experiences=long_experiences,
            job_offer_text="Recherche un expert capable de tout faire sur une seule page."
        )

        print("\n--- Début de la génération asynchrone ---\n")
        background_generate_cv(job_id, request, user.id)
        print("\n--- Fin de la génération ---\n")

        # 5. Vérifier le résultat final
        db.refresh(log_entry)
        print(f"📊 Statut Final en DB: {log_entry.status}")
        
        if log_entry.status == "success":
            print(f"✅ SUCCÈS : Un CV a été validé. Chemin : {log_entry.model}")
        else:
            print(f"❌ ÉCHEC : {log_entry.model}")

    finally:
        db.close()

if __name__ == "__main__":
    test_retry_loop()
