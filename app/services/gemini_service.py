import google.generativeai as genai
from app.config.settings import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        """Inicializa el servicio de Gemini con la API key"""
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def normalize_to_pseudocode(self, natural_language: str) -> str:
        """
        Convierte descripción en lenguaje natural a pseudocódigo estructurado
        
        Args:
            natural_language: Descripción del algoritmo en lenguaje natural
            
        Returns:
            str: Pseudocódigo normalizado siguiendo la gramática establecida
        """
        prompt = f"""
        Convierte la siguiente descripción en lenguaje natural a pseudocódigo siguiendo exactamente esta gramática:

        REGLAS DE SINTAXIS:
        - Los procedimientos se definen como: nombre_procedimiento(parametros) begin ... end
        - Las asignaciones usan el símbolo: variable 🡨 valor
        - Los bucles for: for variable 🡨 inicio to fin do begin ... end
        - Los bucles while: while (condicion) do begin ... end
        - Los condicionales: if (condicion) then begin ... end else begin ... end
        - Los comentarios usan ►
        - Las llamadas a funciones: CALL nombre_funcion(parametros)
        
        DESCRIPCIÓN A CONVERTIR:
        {natural_language}
        
        RESPUESTA (solo el pseudocódigo, sin explicaciones adicionales):
        """
        
        try:
            response = await self._generate_content(prompt)
            return response.strip()
        except Exception as e:
            logger.error(f"Error al normalizar con Gemini: {e}")
            raise Exception(f"Error en la normalización: {str(e)}")
    
    async def correct_pseudocode(self, pseudocode: str, error_details: str) -> str:
        """
        Corrige pseudocódigo que tiene errores sintácticos
        
        Args:
            pseudocode: Pseudocódigo con errores
            error_details: Detalles del error encontrado
            
        Returns:
            str: Pseudocódigo corregido
        """
        prompt = f"""
        El siguiente pseudocódigo tiene errores sintácticos. Corrígelo siguiendo exactamente la gramática establecida:

        GRAMÁTICA REQUERIDA:
        - Procedimientos: nombre_procedimiento(parametros) begin ... end
        - Asignaciones: variable 🡨 valor
        - For: for variable 🡨 inicio to fin do begin ... end
        - While: while (condicion) do begin ... end
        - If: if (condicion) then begin ... end else begin ... end
        - Comentarios: ►
        - Llamadas: CALL nombre_funcion(parametros)
        
        PSEUDOCÓDIGO CON ERRORES:
        {pseudocode}
        
        ERROR DETECTADO:
        {error_details}
        
        PSEUDOCÓDIGO CORREGIDO (solo el código, sin explicaciones):
        """
        
        try:
            response = await self._generate_content(prompt)
            return response.strip()
        except Exception as e:
            logger.error(f"Error al corregir con Gemini: {e}")
            raise Exception(f"Error en la corrección: {str(e)}")
    
    async def _generate_content(self, prompt: str) -> str:
        """
        Método helper para generar contenido con Gemini
        
        Args:
            prompt: Prompt para enviar al modelo
            
        Returns:
            str: Respuesta del modelo
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error en la generación de contenido: {e}")
            raise

# Instancia global del servicio
gemini_service = GeminiService()