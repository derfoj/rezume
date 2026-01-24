from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import jwt
import os
import logging

logger = logging.getLogger(__name__)

# Environment State: 'dev' or 'prod'
ENV_STATE = os.getenv("ENV_STATE", "dev")

# Charge la clé secrète depuis les variables d'environnement
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    if ENV_STATE == "prod":
        logger.critical("❌ CRITICAL: SECRET_KEY is missing in production environment!")
        raise RuntimeError("SECRET_KEY must be set in production.")
    else:
        SECRET_KEY = "CHANGE_THIS_TO_A_REAL_SECRET_IN_PRODUCTION"
        logger.warning("⚠️ WARNING: SECRET_KEY not found. Using default insecure key for development.")

if SECRET_KEY == "CHANGE_THIS_TO_A_REAL_SECRET_IN_PRODUCTION" and ENV_STATE == "prod":
    logger.critical("❌ CRITICAL: Default insecure SECRET_KEY used in production!")
    raise RuntimeError("You must change the default SECRET_KEY in production.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt