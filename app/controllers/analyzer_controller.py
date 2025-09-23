from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["analyzer"])



@router.get("/health")
async def health_check():
    """Endpoint de verificación de salud del servicio"""
    return {
        "status": "healthy",
        "service": "Analizador de Complejidades",
        "version": "1.0.0"
    }
