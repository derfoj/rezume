from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging

logger = logging.getLogger(__name__)

# Use environment variable for DB URL, fallback to local SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./rezume.db")

# Handle Render's Postgres URL and SSL for Neon
if DATABASE_URL and (DATABASE_URL.startswith("postgres://") or DATABASE_URL.startswith("postgresql://")):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    # Neon and Render Postgres often require sslmode=require
    if "sslmode=" not in DATABASE_URL:
        if "?" in DATABASE_URL:
            DATABASE_URL += "&sslmode=require"
        else:
            DATABASE_URL += "?sslmode=require"

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL, 
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=300
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def run_auto_migrations():
    """
    Safely adds missing columns/tables without Alembic for simple SaaS deployment.
    """
    logger.info("Checking for database migrations...")
    with engine.connect() as conn:
        # 1. Add 'role' column to 'users' if missing
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'user';"))
            conn.commit()
            logger.info("Migration: Added 'role' column to 'users'.")
        except Exception:
            pass # Column already exists

        # 2. Add 'openai_api_key' if missing (SaaS ready)
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN openai_api_key VARCHAR;"))
            conn.commit()
        except Exception:
            pass
            
    logger.info("Migrations check complete.")
