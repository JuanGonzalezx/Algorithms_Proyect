"""
Aplicación FastAPI principal
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

from app.api.routes import router as agent_router
from app.api.analyzer_controller import router as analyzer_router
from app.config.settings import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# Crear aplicación FastAPI
app = FastAPI(
    title="Analizador de Complejidades Algorítmicas",
    description="Sistema inteligente para análisis de complejidad computacional de algoritmos en pseudocódigo, asistido por LLMs",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(agent_router, prefix="/api/v1", tags=["agents"])
app.include_router(analyzer_router, prefix="/api/v1", tags=["analyzer"])


@app.get("/", tags=["health"])
async def root():
    """Endpoint raíz - verificación de salud del API."""
    return {
        "message": "API de Análisis de Complejidades Algorítmicas",
        "status": "online",
        "version": "2.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Algorithm Complexity Analyzer",
        "version": "2.0.0"
    }


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