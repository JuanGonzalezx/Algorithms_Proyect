import google.generativeai as genai
from app.config.settings import settings
import asyncio
import logging
import re

logger = logging.getLogger(__name__)

ARROW = "🡨"  # U+1F86A
class GeminiService:
    def __init__(self):
        """Inicializa el servicio de Gemini con la API key desde .env"""
        # La API key se lee automáticamente desde el archivo .env mediante python-decouple
        if not settings.GEMINI_API_KEY:
            raise EnvironmentError(
                "GEMINI_API_KEY no definida. Por favor, configura la variable GEMINI_API_KEY en el archivo .env"
            )
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Modelo vigente
        self.model = genai.GenerativeModel("gemini-2.5-pro")
        logger.info("Servicio Gemini inicializado correctamente")

    async def normalize_to_pseudocode(self, natural_language: str) -> str:
        """
        Convierte descripción en lenguaje natural a pseudocódigo estructurado
        siguiendo la gramática definida en el proyecto.
        """
        # ¡OJO!: llaves literales como {{atributos}} para que no fallen los f-strings
        prompt = f"""
Convierte la siguiente descripción en pseudocódigo siguiendo EXACTAMENTE esta gramática:

REGLAS PRINCIPALES:
- Procedimientos: nombre_procedimiento(parametros) \nbegin ... end
- Asignaciones: variable {ARROW} valor
- FOR: for variable {ARROW} inicio to fin do \nbegin ... end
- WHILE: while (condicion) do \nbegin ... end
- REPEAT: repeat ... until (condicion)
- IF: if (condicion) then \nbegin ... end else \nbegin ... end
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

    async def generate_python_code(self, natural_language: str) -> str:
        """
        Genera una implementación en Python a partir de la descripción en lenguaje natural.
        La respuesta debe ser SOLO el código Python (sin explicaciones ni markdown).
        """
        prompt = f"""
Eres un asistente que convierte descripciones en implementaciones en Python.

Requisitos:
- Devuelve SOLO código Python válido; no añadas explicaciones, ni títulos, ni Markdown.
- Define una o más funciones/classes necesarias para implementar la descripción.
- Añade un docstring breve en la función principal si procede.
- Evita entradas interactivas (no input()).
- Si el algoritmo usa estructuras de datos, usa construcciones estándar de Python.

DESCRIPCIÓN:
{natural_language}

RESPUESTA:
(Solo el código Python, sin explicaciones, sin ```)
"""
        try:
            raw = await self._generate_content(prompt)
            # A veces Gemini devuelve texto con contenido adicional; limpiamos espacios extra
            return raw.strip()
        except Exception as e:
            logger.error(f"Error al generar Python con Gemini: {e}")
            raise Exception(f"Error en la generación de código: {str(e)}")

    

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
