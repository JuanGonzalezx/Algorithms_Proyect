from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.controllers.analyzer_controller import router as analyzer_router
from app.config.settings import settings
import logging
import uvicorn

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
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(analyzer_router)

@app.get("/")
async def root():
    """Endpoint raíz con información del servicio"""
    return {
        "service": "Analizador de Complejidades Algorítmicas",
        "version": "1.0.0",
        "description": "Sistema para análisis automático de complejidad computacional",
        "docs": "/docs",
        "health": "/api/v1/health",
        "endpoints": {
            "classify": "/api/v1/classify",
            "normalize": "/api/v1/normalize", 
            "parse": "/api/v1/parse"
        }
    }

@app.on_event("startup")
async def startup_event():
    """Eventos de inicio de la aplicación"""
    logger.info("🚀 Iniciando Analizador de Complejidades Algorítmicas")
    logger.info(f"📡 Servidor configurado en {settings.HOST}:{settings.PORT}")
    logger.info(f"🔧 Modo debug: {settings.DEBUG}")
    
    # Verificar configuración de Gemini
    if not settings.GEMINI_API_KEY:
        logger.warning("⚠️  GEMINI_API_KEY no está configurada")
    else:
        logger.info("✅ API de Gemini configurada correctamente")

@app.on_event("shutdown")
async def shutdown_event():
    """Eventos de cierre de la aplicación"""
    logger.info("🛑 Cerrando Analizador de Complejidades Algorítmicas")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )