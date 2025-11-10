"""
Aplicación FastAPI principal con arquitectura modular basada en agentes.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.routes import router as agent_router
from app.controllers.analyzer_controller import router as analyzer_router
from app.config.settings import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """
    Factory para crear la aplicación FastAPI.
    
    Returns:
        FastAPI: Instancia configurada de la aplicación
    """
    app = FastAPI(
        title="Analizador de Complejidades Algorítmicas",
        description="Sistema inteligente para análisis de complejidad computacional de algoritmos en pseudocódigo, asistido por LLMs y agentes especializados",
        version="2.0.0",
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

    # Incluir routers
    app.include_router(agent_router)  # Nuevas rutas basadas en agentes
    app.include_router(analyzer_router)  # Rutas legacy existentes

    @app.get("/")
    async def root():
        """Endpoint raíz con información del servicio"""
        return {
            "service": "Analizador de Complejidades Algorítmicas",
            "version": "2.0.0",
            "description": "Sistema para análisis automático de complejidad computacional con arquitectura de agentes",
            "docs": "/docs",
            "endpoints": {
                "health": "/api/v1/health",
                "validate_syntax": "/api/v1/validate-syntax",
                # Legacy endpoints
                "classify": "/api/v1/classify",
                "normalize": "/api/v1/normalize",
                "parse": "/api/v1/parse"
            },
            "agents": [
                "syntax_validator"
            ]
        }

    @app.on_event("startup")
    async def startup_event():
        """Evento de inicio de la aplicación"""
        logger.info("🚀 Iniciando aplicación...")
        logger.info("📦 Cargando agentes...")
        
        try:
            # Pre-cargar el agente de validación sintáctica
            from app.modules.syntax_validator.agent import get_syntax_validator
            validator = get_syntax_validator()
            logger.info("✅ Agente de validación sintáctica cargado")
        except Exception as e:
            logger.error(f"❌ Error al cargar agente: {e}")
        
        # Mostrar información de las API keys de Gemini
        try:
            from app.services.gemini_service import gemini_service
            num_keys = len(gemini_service.api_keys)
            current_key_masked = gemini_service.api_keys[gemini_service.current_key_index][-4:]
            logger.info(f"🔑 Gemini configurado con {num_keys} API key(s)")
            logger.info(f"🔑 Key activa: ****{current_key_masked}")
        except Exception as e:
            logger.warning(f"⚠️  No se pudo cargar información de Gemini: {e}")
        
        logger.info("✨ Aplicación iniciada correctamente")

    @app.on_event("shutdown")
    async def shutdown_event():
        """Evento de cierre de la aplicación"""
        logger.info("👋 Cerrando aplicación...")

    return app


# Crear instancia de la aplicación
app = create_app()
