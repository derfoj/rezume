import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api import app
from src.core.database import Base, get_db
from src.models.user import User
from src.core.security import get_password_hash

# Setup base de données de test (SQLite en mémoire)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"
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

def test_register_user():
    """Vérifie l'inscription d'un nouvel utilisateur"""
    response = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "password123", "full_name": "Test User"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_success():
    """Vérifie la connexion avec des identifiants valides (JSON)"""
    # 1. Créer l'utilisateur
    client.post(
        "/api/auth/register",
        json={"email": "login@example.com", "password": "securepassword", "full_name": "Login User"}
    )
    # 2. Se connecter en envoyant du JSON (pas du form data)
    response = client.post(
        "/api/auth/login",
        json={"email": "login@example.com", "password": "securepassword"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["message"] == "Login successful"

def test_admin_access_denied_for_regular_user():
    """Vérifie qu'un utilisateur standard ne peut pas accéder aux routes admin"""
    # 1. Inscription & Connexion d'un utilisateur standard
    client.post("/api/auth/register", json={"email": "user@example.com", "password": "password", "full_name": "Regular"})
    login_res = client.post("/api/auth/login", json={"email": "user@example.com", "password": "password"})
    token = login_res.json()["access_token"]
    
    # 2. Tentative d'accès à la liste des utilisateurs (protégée par get_admin_user)
    response = client.get("/api/auth/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403 # Forbidden

def test_admin_access_allowed_for_admin_user():
    """Vérifie qu'un admin peut accéder aux routes admin"""
    # 1. Créer manuellement un admin en base
    db = TestingSessionLocal()
    admin_user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("adminpass"),
        role="admin"
    )
    db.add(admin_user)
    db.commit()
    db.close()

    # 2. Login
    login_res = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "adminpass"})
    token = login_res.json()["access_token"]

    # 3. Accès admin
    response = client.get("/api/auth/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) >= 1
