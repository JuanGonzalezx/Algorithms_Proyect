import google.generativeai as genai
from app.config.settings import settings
import asyncio
import logging
import re

logger = logging.getLogger(__name__)

ARROW = "🡨"  # U+1F86A
class GeminiService:
    def __init__(self):
        """Inicializa el servicio de Gemini con la API key"""
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Modelo vigente
        self.model = genai.GenerativeModel("gemini-2.5-pro")

    async def normalize_to_pseudocode(self, natural_language: str) -> str:
        """
        Convierte descripción en lenguaje natural a pseudocódigo estructurado
        siguiendo la gramática definida en el proyecto.
        """
        # ¡OJO!: llaves literales como {{atributos}} para que no fallen los f-strings
        prompt = f"""
Convierte la siguiente descripción en pseudocódigo siguiendo EXACTAMENTE esta gramática:

REGLAS PRINCIPALES:
- Procedimientos: nombre_procedimiento(parametros) begin ... end
- Asignaciones: variable {ARROW} valor
- FOR: for variable {ARROW} inicio to fin do begin ... end
- WHILE: while (condicion) do begin ... end
- REPEAT: repeat ... until (condicion)
- IF: if (condicion) then begin ... end else begin ... end
- Comentarios inician con ►
- Llamadas: CALL nombre_funcion(parametros)
- Acceso a arreglos: A[i], subarreglos: A[1..j]
- Variables locales declaradas después de begin
- Objetos: Clase nombre {{atributos}}
- Valores booleanos: T, F
- Operadores: and, or, not, <, >, ≤, ≥, =, ≠, +, -, *, /, mod, div

DESCRIPCIÓN:
{natural_language}

RESPUESTA:
(Solo el pseudocódigo, sin explicaciones, sin markdown, sin ```)
"""
        try:
            raw = await self._generate_content(prompt)
            return raw
        except Exception as e:
            logger.error(f"Error al normalizar con Gemini: {e}")
            raise Exception(f"Error en la normalización: {str(e)}")

    

    async def _generate_content(self, prompt: str) -> str:
        """
        Método helper: usa Gemini de forma asíncrona sin bloquear FastAPI.
        """
        try:
            def _call():
                resp = self.model.generate_content(prompt)
                return resp.text if hasattr(resp, "text") else ""
            return await asyncio.to_thread(_call)
        except Exception as e:
            logger.error(f"Error en la generación de contenido: {e}")
            raise

# Instancia global
gemini_service = GeminiService()
