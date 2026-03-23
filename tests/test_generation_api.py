import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from api import app
from src.core.database import get_db, Base
from src.models.user import User
from src.core.security import get_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_gen.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def get_auth_token(email="gen@example.com"):
    """Helper to get a valid JWT token"""
    client.post("/api/auth/register", json={"email": email, "password": "pass", "full_name": "Gen User"})
    login_res = client.post("/api/auth/login", json={"email": email, "password": "pass"})
    return login_res.json()["access_token"]

# --- 1. Test de l'Endpoint /api/generate-cv ---
@patch("src.api.generation.GeneratorAgent")
def test_generate_cv_endpoint(mock_agent_class):
    """Vérifie que l'endpoint de génération lance bien la tâche et renvoie un job_id"""
    # Mock de l'agent et de sa méthode generate_latex_source
    mock_agent = MagicMock()
    mock_agent.generate_latex_source.return_value = "\\documentclass{article}\\begin{document}Test\\end{document}"
    mock_agent_class.return_value = mock_agent
    
    token = get_auth_token()
    
    response = client.post(
        "/api/generate-cv",
        json={
            "experiences": [{"title": "Software Engineer", "company": "Tech Corp", "description": "Dev"}],
            "job_offer_text": "Need a dev",
            "latex_only": True
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["message"] == "Génération de la source LaTeX lancée."

# --- 2. Test du Statut du Job & Sécurité IDOR ---
def test_get_job_status_and_security():
    """Vérifie qu'on peut récupérer le statut d'un job et que l'IDOR est bloqué"""
    token_user1 = get_auth_token("user1@example.com")
    token_user2 = get_auth_token("user2@example.com")
    
    # User 1 crée un job
    gen_res = client.post(
        "/api/generate-cv",
        json={"experiences": []},
        headers={"Authorization": f"Bearer {token_user1}"}
    )
    job_id = gen_res.json()["job_id"]
    
    # User 1 vérifie son propre statut -> OK
    status_res = client.get(f"/api/status/{job_id}", headers={"Authorization": f"Bearer {token_user1}"})
    assert status_res.status_code == 200
    
    # User 2 essaie de voir le statut de User 1 -> 403 Forbidden
    status_res_unauthorized = client.get(f"/api/status/{job_id}", headers={"Authorization": f"Bearer {token_user2}"})
    assert status_res_unauthorized.status_code == 403

# --- 3. Test de la Récupération de la Source LaTeX & Sécurité ---
@patch("src.api.generation.background_generate_cv")
def test_get_latex_source_security(mock_bg_task):
    """Vérifie la sécurité lors de la récupération de la source LaTeX"""
    token_user1 = get_auth_token("latex1@example.com")
    token_user2 = get_auth_token("latex2@example.com")
    
    # 1. Simuler un job pour User 1 (ID 1)
    db = TestingSessionLocal()
    from src.models.usage import UsageLog
    import os
    
    fake_tex_path = "outputs/generated_cvs/999/cv_999.tex"
    os.makedirs(os.path.dirname(fake_tex_path), exist_ok=True)
    with open(fake_tex_path, "w") as f:
        f.write("User 1 Secret Content")
    
    # Note: user_id=1 car c'est le premier créé dans cette transaction
    log = UsageLog(id=999, user_id=1, action="cv_generation", status="success", model=fake_tex_path)
    db.add(log)
    db.commit()
    db.close()
    
    # 2. User 1 récupère son propre LaTeX -> OK
    response = client.get("/api/latex/999", headers={"Authorization": f"Bearer {token_user1}"})
    assert response.status_code == 200
    
    # 3. User 2 essaie de voler le LaTeX de User 1 -> 403
    response_unauthorized = client.get("/api/latex/999", headers={"Authorization": f"Bearer {token_user2}"})
    assert response_unauthorized.status_code == 403
    
    # Cleanup
    if os.path.exists("outputs/generated_cvs/999"):
        import shutil
        shutil.rmtree("outputs/generated_cvs/999")

# --- 4. Test de Sécurité (Accès non authentifié) ---
def test_generate_cv_unauthenticated():
    """Vérifie que l'accès sans token est refusé"""
    response = client.post("/api/generate-cv", json={"experiences": []})
    assert response.status_code == 401
