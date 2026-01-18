# api.py (Main Application File)
import uvicorn
import sys
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.database import engine, Base
from src.api import auth, analysis, generation, profile as profile_api
from src.core.orchestration import parser_agent

# --- Database Initialization ---
# For development, we create tables on startup. In prod, use Alembic.
Base.metadata.create_all(bind=engine)

# --- FastAPI App Initialization ---
app = FastAPI(title="reZume API")

# --- Middleware ---
# Load allowed origins from environment variable or use defaults
origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173,http://localhost:5174,http://127.0.0.1:3000,http://127.0.0.1:5173")
origins = [origin.strip() for origin in origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(profile_api.router, prefix="/api", tags=["Profile"])
app.include_router(analysis.router, prefix="/api", tags=["Analysis"])
app.include_router(generation.router, prefix="/api", tags=["Generation"])

# --- Root Endpoint ---
@app.get("/")
def health_check():
    """Health check endpoint to verify that the backend is running."""
    return {
        "status": "Online",
        "backend": "Python/FastAPI",
        "database": "SQLite",
        "ai_ready": parser_agent is not None
    }

# --- Main Entry Point ---
if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)