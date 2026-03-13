from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
import logging
import os

logger = logging.getLogger("reZume.errors")

async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch-all handler for any unhandled exception.
    Prevents the server from crashing and returns a standard JSON error.
    """
    env = os.getenv("ENV_STATE", "dev")
    logger.error(f"Global Exception: {str(exc)}", exc_info=True)
    
    error_content = {
        "detail": "Une erreur interne inattendue est survenue.",
        "code": "INTERNAL_SERVER_ERROR"
    }
    
    # Show error details only if not in production
    if env != "prod":
        error_content["original_error"] = str(exc)
        
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_content
    )

async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Handles Database errors specifically.
    """
    env = os.getenv("ENV_STATE", "dev")
    logger.error(f"Database Error: {str(exc)}", exc_info=True)
    
    error_content = {
        "detail": "Le service de base de données est temporairement indisponible.",
        "code": "DATABASE_ERROR"
    }
    
    if env != "prod":
        error_content["original_error"] = str(exc)

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=error_content
    )
