# api.py (Main Application File)
import uvicorn
import sys
import os
import logging
import gc
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from src.core.database import engine, Base, run_auto_migrations
from src.models.user import User
from src.models.profile import Experience, Education, Skill, Language
from src.models.usage import UsageLog

from src.api import auth, analysis, generation, profile as profile_api, admin as admin_api
from src.core.orchestration import parser_agent
from src.core.error_handlers import global_exception_handler, database_exception_handler

# --- Environment State ---
ENV = os.getenv("ENV_STATE", "dev")

# --- Rate Limiter ---
limiter = Limiter(key_func=get_remote_address, enabled=(ENV == "prod"))

# --- Database & Auto-Migration ---
logger.info("Initializing Database...")
try:
    Base.metadata.create_all(bind=engine)
    run_auto_migrations() # AUTOMATICALLY adds missing columns
except Exception as e:
    logger.error(f"Migration error: {e}")

# --- FastAPI App ---
app = FastAPI(
    title="reZume API",
    docs_url="/docs" if ENV != "prod" else None,
    redoc_url="/redoc" if ENV != "prod" else None
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- Memory Watchdog (Middleware) ---
@app.middleware("http")
async def memory_cleanup_middleware(request: Request, call_next):
    response = await call_next(request)
    # Force GC collect after each request to keep RAM low on Render Free
    if request.url.path.startswith("/api/generate") or request.url.path.startswith("/api/analyze"):
        gc.collect()
    return response

# --- Middleware CORS ---
origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173")
origins = [origin.strip() for origin in origins_str.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Exception Handlers ---
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# --- Router Registration ---
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(profile_api.router, prefix="/api", tags=["Profile"])
app.include_router(analysis.router, prefix="/api", tags=["Analysis"])
app.include_router(generation.router, prefix="/api", tags=["Generation"])
app.include_router(admin_api.router, prefix="/api/admin", tags=["Admin"])

@app.get("/")
def health_check():
    return {"status": "Online"} if ENV == "prod" else {"status": "Online", "db": "Active", "env": ENV}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=(ENV == "dev"))
