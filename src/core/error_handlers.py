from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger("reZume.errors")

async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch-all handler for any unhandled exception.
    Prevents the server from crashing and returns a standard JSON error.
    """
    logger.error(f"Global Exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Une erreur interne inattendue est survenue.",
            "code": "INTERNAL_SERVER_ERROR",
            "original_error": str(exc) if "dev" in str(request.url) else None # Show error details only in dev if needed, or secure it
        }
    )

async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Handles Database errors specifically.
    """
    logger.error(f"Database Error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "detail": "Le service de base de données est temporairement indisponible.",
            "code": "DATABASE_ERROR"
        }
    )
