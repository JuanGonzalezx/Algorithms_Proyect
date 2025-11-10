import google.generativeai as genai
from app.config.settings import settings
import asyncio
import logging
import re
import time
from typing import List, Optional

logger = logging.getLogger(__name__)

ARROW = "🡨"  # U+1F86A

class GeminiService:
    def __init__(self):
        """Inicializa el servicio de Gemini con rotación de múltiples API keys"""
        # Cargar todas las API keys disponibles
        self.api_keys = self._load_api_keys()
        
        if not self.api_keys:
            raise EnvironmentError(
                "No se encontraron API keys válidas. Por favor, configura GEMINI_API_KEY o GEMINI_API_KEYS en el archivo .env"
            )
        
        # Estado de rotación
        self.current_key_index = 0
        self.failed_keys = set()  # Keys que han fallado por quota
        
        # Configurar con la primera key
        self._configure_current_key()
        
        # Configuración de reintentos y timeout desde .env
        self.max_retries = settings.GEMINI_MAX_RETRIES
        self.timeout = settings.GEMINI_TIMEOUT
        self.base_delay = settings.GEMINI_BASE_DELAY
        
        logger.info("Servicio Gemini inicializado correctamente")
        logger.info(f"  🔑 API Keys disponibles: {len(self.api_keys)}")
        logger.info(f"  ⏱️  Timeout: {self.timeout}s")
        logger.info(f"  🔄 Reintentos: {self.max_retries}")
        logger.info(f"  ⏳ Delay base: {self.base_delay}s")
    
    def _load_api_keys(self) -> List[str]:
        """
        Carga todas las API keys disponibles desde el .env
        
        Soporta dos formatos:
        1. GEMINI_API_KEY=key1 (una sola key)
        2. GEMINI_API_KEYS=key1,key2,key3 (múltiples keys separadas por coma)
        
        Returns:
            Lista de API keys válidas (sin duplicados ni vacías)
        """
        keys = []
        
        # Intentar cargar múltiples keys
        if hasattr(settings, 'GEMINI_API_KEYS') and settings.GEMINI_API_KEYS:
            keys_str = settings.GEMINI_API_KEYS
            keys = [k.strip() for k in keys_str.split(',') if k.strip()]
        
        # Si no hay múltiples, intentar la key individual
        if not keys and settings.GEMINI_API_KEY:
            keys = [settings.GEMINI_API_KEY.strip()]
        
        # Filtrar keys vacías y eliminar duplicados
        keys = list(set([k for k in keys if k]))
        
        logger.info(f"📋 Cargadas {len(keys)} API key(s)")
        return keys
    
    def _configure_current_key(self):
        """Configura Gemini con la API key actual"""
        if self.current_key_index >= len(self.api_keys):
            self.current_key_index = 0
        
        current_key = self.api_keys[self.current_key_index]
        genai.configure(api_key=current_key)
        # Usando gemini-2.5-flash (modelo actualizado de Google)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Mostrar solo los últimos 4 caracteres por seguridad
        masked_key = "***" + current_key[-4:] if len(current_key) > 4 else "***"
        logger.info(f"🔑 Usando API key #{self.current_key_index + 1}/{len(self.api_keys)}: {masked_key}")
    
    def _rotate_to_next_key(self) -> bool:
        """
        Rota a la siguiente API key disponible
        
        Returns:
            True si se pudo rotar, False si no hay más keys disponibles
        """
        # Marcar la key actual como fallida
        self.failed_keys.add(self.current_key_index)
        
        # Buscar la siguiente key no fallida
        attempts = 0
        while attempts < len(self.api_keys):
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
            
            if self.current_key_index not in self.failed_keys:
                logger.warning(f"🔄 Rotando a API key #{self.current_key_index + 1}/{len(self.api_keys)}")
                self._configure_current_key()
                return True
            
            attempts += 1
        
        # Todas las keys han fallado
        logger.error("❌ Todas las API keys han excedido su cuota")
        return False

    async def normalize_to_pseudocode(self, natural_language: str, hint: str = None) -> str:
        """
        Convierte descripción en lenguaje natural a pseudocódigo estructurado
        siguiendo la gramática definida en el proyecto.
        
        Args:
            natural_language: Texto en lenguaje natural o código con errores
            hint: Instrucción adicional para el modelo (opcional)
        """
        # ¡OJO!: llaves literales como {{atributos}} para que no fallen los f-strings
        prompt = f"""
Convierte la siguiente descripción en PSEUDOCÓDIGO ESTRUCTURADO siguiendo EXACTAMENTE estas reglas:

SINTAXIS OBLIGATORIA:
1. PROCEDIMIENTOS: Siempre usar "begin" y "end"
   procedimiento_nombre(parametros)
   begin
       instrucciones
   end

2. FOR: Siempre terminar con "do" seguido de "begin...end"
   for variable {ARROW} inicio to fin do
   begin
       instrucciones
   end

3. WHILE: Siempre terminar con "do" seguido de "begin...end"
   while (condicion) do
   begin
       instrucciones
   end

4. REPEAT-UNTIL: DEBE usar "begin" inmediatamente después de "repeat"
   repeat
   begin
       instrucciones
   end
   until (condicion)

5. IF-THEN-ELSE: Siempre usar "begin...end" en bloques
   if (condicion) then
   begin
       instrucciones
   end
   else
   begin
       instrucciones
   end

6. ASIGNACIONES: Usar flecha {ARROW}
   variable {ARROW} valor

7. ARRAYS: A[i] o A[1..n]

8. OPERADORES LÓGICOS: Siempre en minúsculas
   - and (conjunción)
   - or (disyunción)
   - not (negación)
   Ejemplo: if (i > 0 and i < n) then

EJEMPLOS CORRECTOS:

Ejemplo 1 - Burbuja:
burbuja(A, n)
begin
    for i {ARROW} 1 to n-1 do
    begin
        for j {ARROW} 1 to n-i do
        begin
            if (A[j] > A[j+1]) then
            begin
                temp {ARROW} A[j]
                A[j] {ARROW} A[j+1]
                A[j+1] {ARROW} temp
            end
        end
    end
end

Ejemplo 2 - Con REPEAT:
buscar(A, n, x)
begin
    i {ARROW} 1
    repeat
    begin
        if (A[i] = x) then
        begin
            return i
        end
        i {ARROW} i + 1
    end
    until (i > n)
    return -1
end

Ejemplo 3 - Inserción (con operador lógico):
insercion(A, n)
begin
    for i {ARROW} 2 to n do
    begin
        clave {ARROW} A[i]
        j {ARROW} i - 1
        while (j > 0 and A[j] > clave) do
        begin
            A[j+1] {ARROW} A[j]
            j {ARROW} j - 1
        end
        A[j+1] {ARROW} clave
    end
end

ERRORES COMUNES A EVITAR:
❌ NUNCA escribir "repeat" sin "begin" después
❌ NUNCA omitir "begin...end" en loops o condicionales
❌ NUNCA usar ":" para asignaciones (usar {ARROW})
❌ NUNCA mezclar español e inglés en palabras clave
❌ NUNCA usar AND/OR/NOT en MAYÚSCULAS (usar: and, or, not en minúsculas)
"""
        
        # Agregar hint si se proporciona
        if hint:
            prompt += f"\n{hint}\n"
        
        prompt += f"""
AHORA CONVIERTE:
{natural_language}

RESPUESTA (solo pseudocódigo, sin explicaciones, sin markdown, sin ```):
"""
        try:
            logger.info(f"📤 Enviando a Gemini... (prompt: {len(prompt)} chars)")
            raw = await self._generate_content(prompt)
            logger.info(f"📥 Respuesta de Gemini recibida: {len(raw)} chars")
            return raw
        except Exception as e:
            logger.error(f"❌ Error al normalizar con Gemini: {e}")
            logger.error(f"   Tipo: {type(e).__name__}")
            import traceback
            logger.error(f"   Traceback: {traceback.format_exc()}")
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

RESTRICCIONES IMPORTANTES:
- NO uses tuple unpacking en asignaciones (NO: a, b = b, a)
- Para intercambiar valores, usa una variable temporal:
  temp = a
  a = b
  b = temp
- NO uses asignaciones múltiples (NO: x = y = z = 0)
- Usa asignaciones simples una por una

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
        Método helper: usa Gemini de forma asíncrona con timeout, reintentos y rotación de keys.
        
        - Timeout: 60 segundos
        - Reintentos: 3 intentos con backoff exponencial (2s, 4s, 8s)
        - Rotación automática de API keys si se detecta error 429 (quota exceeded)
        - Reintentos automáticos para errores 500 (server errors)
        """
        last_error = None
        keys_rotated = 0  # Contador de rotaciones de keys
        
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"🔄 Intento {attempt}/{self.max_retries} - Llamando a Gemini...")
                
                def _call():
                    resp = self.model.generate_content(prompt)
                    return resp.text if hasattr(resp, "text") else ""
                
                # Ejecutar con timeout
                result = await asyncio.wait_for(
                    asyncio.to_thread(_call),
                    timeout=self.timeout
                )
                
                logger.info(f"✅ Respuesta recibida exitosamente (intento {attempt})")
                return result
                
            except asyncio.TimeoutError:
                last_error = f"Timeout después de {self.timeout} segundos"
                logger.warning(f"⏱️  Timeout en intento {attempt}/{self.max_retries}")
                
                if attempt < self.max_retries:
                    delay = self.base_delay * (2 ** (attempt - 1))
                    logger.info(f"⏳ Esperando {delay}s antes de reintentar...")
                    await asyncio.sleep(delay)
                    
            except Exception as e:
                error_str = str(e)
                last_error = error_str
                
                # ==================== LOGGING DETALLADO DEL ERROR ====================
                logger.error("=" * 80)
                logger.error("🔴 ERROR CRUDO DE GEMINI (sin procesar):")
                logger.error(f"Tipo de excepción: {type(e).__name__}")
                logger.error(f"Mensaje completo: {error_str}")
                logger.error(f"Representación: {repr(e)}")
                
                # Si el error tiene atributos adicionales, mostrarlos
                if hasattr(e, '__dict__'):
                    logger.error(f"Atributos del error: {e.__dict__}")
                
                # Mostrar traceback completo
                import traceback
                logger.error("Traceback completo:")
                logger.error(traceback.format_exc())
                logger.error("=" * 80)
                # ======================================================================
                
                # Detectar error 429 (quota exceeded)
                is_429_error = "429" in error_str or "quota exceeded" in error_str.lower()
                
                # Detectar errores 500 (server errors)
                is_500_error = "500" in error_str or "internal error" in error_str.lower()
                
                # Detectar errores 503 (service unavailable)
                is_503_error = "503" in error_str or "service unavailable" in error_str.lower()
                
                if is_429_error:
                    logger.warning(f"⚠️  Error 429 (Quota Exceeded) detectado")
                    
                    # Intentar rotar a la siguiente key
                    if self._rotate_to_next_key():
                        keys_rotated += 1
                        logger.info(f"✅ Rotación exitosa (#{keys_rotated}). Reintentando inmediatamente...")
                        # No incrementar 'attempt', reintentar inmediatamente con la nueva key
                        continue
                    else:
                        # No hay más keys disponibles
                        logger.error("❌ No hay más API keys disponibles. Todas han excedido su cuota.")
                        raise Exception(
                            f"Todas las API keys ({len(self.api_keys)}) han excedido su cuota diaria. "
                            f"Por favor, espera o agrega más keys al archivo .env"
                        )
                
                elif is_500_error:
                    logger.warning(f"⚠️  Error 500 en intento {attempt}/{self.max_retries}: {error_str}")
                    
                    if attempt < self.max_retries:
                        delay = self.base_delay * (2 ** (attempt - 1))
                        logger.info(f"⏳ Esperando {delay}s antes de reintentar...")
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"❌ Error 500 persistente después de {self.max_retries} intentos")
                
                elif is_503_error:
                    logger.warning(f"⚠️  Error 503 (Service Unavailable) detectado")
                    logger.warning(f"Esto puede indicar que el modelo no existe o no está disponible")
                    logger.warning(f"Modelo actual: gemini-2.5-flash")
                    logger.warning(f"Modelos válidos: gemini-1.5-flash, gemini-1.5-pro")
                    raise
                
                else:
                    # Otros errores (403, etc.) no reintentamos
                    logger.error(f"❌ Error no recuperable: {error_str}")
                    raise
        
        # Si llegamos aquí, fallaron todos los intentos
        logger.error(f"❌ Fallaron todos los {self.max_retries} intentos")
        raise Exception(f"Error en la generación de contenido después de {self.max_retries} intentos: {last_error}")

# Instancia global
gemini_service = GeminiService()
