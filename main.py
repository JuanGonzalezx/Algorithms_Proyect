"""
Punto de entrada principal de la aplicación.
Importa la aplicación FastAPI desde app/main.py
"""
from app.main import app
from app.config.settings import settings
import uvicorn
import logging

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("🚀 Iniciando Analizador de Complejidades Algorítmicas")
    logger.info(f"📡 Servidor en {settings.HOST}:{settings.PORT}")
    logger.info(f"🔧 Modo debug: {settings.DEBUG}")
    
    # Verificar configuración de Gemini
    if not settings.GEMINI_API_KEYS and not settings.GEMINI_API_KEY:
        logger.warning("⚠️  No hay API keys de Gemini configuradas")
    else:
        logger.info("✅ API de Gemini configurada")
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )