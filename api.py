# api.py (Main Application File)
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- Local Router Imports ---
from api import analysis, generation
from src.core.orchestration import parser_agent

# --- FastAPI App Initialization ---
app = FastAPI(title="reZume API")

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(analysis.router, prefix="/api", tags=["Analysis"])
app.include_router(generation.router, prefix="/api", tags=["Generation"])

# --- Root Endpoint ---
@app.get("/")
def health_check():
    """Health check endpoint to verify that the backend is running."""
    return {
        "status": "Online",
        "backend": "Python/FastAPI",
        "ai_ready": parser_agent is not None
    }

# --- Main Entry Point ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
