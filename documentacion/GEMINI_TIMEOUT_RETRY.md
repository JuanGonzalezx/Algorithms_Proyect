# Mejoras en Gemini Service: Timeout y Reintentos Automáticos

## 📋 Resumen de Cambios

Se implementó un sistema robusto de **timeout** y **reintentos automáticos** para manejar errores temporales de la API de Gemini.

## ✨ Características Implementadas

### 1. **Timeout Configurable**
- ⏱️ **60 segundos** por defecto (vs. ~30s anterior)
- Previene bloqueos indefinidos cuando Gemini no responde
- Configurable desde `.env`: `GEMINI_TIMEOUT=60`

### 2. **Reintentos Automáticos**
- 🔄 **3 intentos** por defecto
- Backoff exponencial: 2s → 4s → 8s entre intentos
- Configurable desde `.env`:
  - `GEMINI_MAX_RETRIES=3`
  - `GEMINI_BASE_DELAY=2`

### 3. **Manejo Inteligente de Errores**

| Error | Comportamiento |
|-------|---------------|
| **500 Internal Server Error** | ✅ Se reintenta automáticamente |
| **Timeout** | ✅ Se reintenta automáticamente |
| **403 Forbidden** (API Key inválida) | ❌ Falla inmediatamente |
| **429 Too Many Requests** (límite de cuota) | ❌ Falla inmediatamente |

### 4. **Logging Detallado**
```
🔄 Intento 1/3 - Llamando a Gemini...
✅ Respuesta recibida exitosamente (intento 1)

⚠️  Error 500 en intento 1/3: 500 An internal error...
⏳ Esperando 2s antes de reintentar...
🔄 Intento 2/3 - Llamando a Gemini...
```

## 📁 Archivos Modificados

### 1. `app/services/gemini_service.py`
**Cambios principales:**
```python
class GeminiService:
    def __init__(self):
        # Configuración desde .env
        self.max_retries = settings.GEMINI_MAX_RETRIES  # 3
        self.timeout = settings.GEMINI_TIMEOUT           # 60s
        self.base_delay = settings.GEMINI_BASE_DELAY     # 2s
    
    async def _generate_content(self, prompt: str) -> str:
        """Con timeout y reintentos automáticos"""
        for attempt in range(1, self.max_retries + 1):
            try:
                # Ejecutar con timeout
                result = await asyncio.wait_for(
                    asyncio.to_thread(_call),
                    timeout=self.timeout
                )
                return result
            except asyncio.TimeoutError:
                # Reintentar con backoff exponencial
                delay = self.base_delay * (2 ** (attempt - 1))
                await asyncio.sleep(delay)
            except Exception as e:
                # Solo reintentar errores 500
                if "500" in str(e):
                    await asyncio.sleep(delay)
                else:
                    raise  # Otros errores fallan inmediatamente
```

### 2. `app/config/settings.py`
```python
class Settings:
    # Nuevas configuraciones
    GEMINI_TIMEOUT: int = config("GEMINI_TIMEOUT", default=60, cast=int)
    GEMINI_MAX_RETRIES: int = config("GEMINI_MAX_RETRIES", default=3, cast=int)
    GEMINI_BASE_DELAY: int = config("GEMINI_BASE_DELAY", default=2, cast=int)
```

### 3. `.env`
```properties
# Configuración de Gemini (timeout y reintentos)
GEMINI_TIMEOUT=60
GEMINI_MAX_RETRIES=3
GEMINI_BASE_DELAY=2
```

### 4. `app/api/routes.py`
```python
# Ahora retorna error HTTP 503 si Gemini falla después de todos los intentos
except Exception as gemini_error:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "message": "El servicio de normalización no está disponible",
            "error": str(gemini_error),
            "suggestion": "Proporciona pseudocódigo o intenta nuevamente"
        }
    )
```

## 🎯 Casos de Uso

### Caso 1: Error 500 Temporal (se recupera)
```
Intento 1: Error 500 → Espera 2s
Intento 2: Error 500 → Espera 4s
Intento 3: ✅ Éxito
```

### Caso 2: Error 500 Persistente
```
Intento 1: Error 500 → Espera 2s
Intento 2: Error 500 → Espera 4s
Intento 3: Error 500
❌ Retorna HTTP 503 al usuario
```

### Caso 3: API Key Inválida
```
Intento 1: Error 403 (Forbidden)
❌ Falla inmediatamente (no reintenta)
```

### Caso 4: Timeout en Red Lenta
```
Intento 1: Timeout (60s) → Espera 2s
Intento 2: ✅ Éxito
```

## 🔧 Configuración Personalizada

Para ajustar el comportamiento, edita `.env`:

```properties
# Más agresivo (respuestas rápidas, menos tolerancia)
GEMINI_TIMEOUT=30
GEMINI_MAX_RETRIES=2
GEMINI_BASE_DELAY=1

# Más conservador (mayor tolerancia a errores)
GEMINI_TIMEOUT=90
GEMINI_MAX_RETRIES=5
GEMINI_BASE_DELAY=3
```

## 📊 Patrón de Delays

Con `GEMINI_BASE_DELAY=2`:
- Intento 1 → Falla → Espera **2s**
- Intento 2 → Falla → Espera **4s**
- Intento 3 → Falla → Espera **8s**
- Intento 4 → ...

**Total tiempo máximo**: `60s + 2s + 60s + 4s + 60s = 186s` (3 minutos aprox.)

## ✅ Testing

Ejecuta las pruebas:
```bash
python test_gemini_retry.py
```

Verifica que:
- ✅ Timeout está configurado (60s)
- ✅ Reintentos están habilitados (3)
- ✅ Backoff exponencial funciona (2s, 4s, 8s)

## 🚀 Próximos Pasos

1. ✅ Timeout implementado
2. ✅ Reintentos automáticos para errores 500
3. ✅ Backoff exponencial
4. ✅ Configuración desde .env
5. ⏭️ Monitoreo de métricas (opcional)
6. ⏭️ Circuit breaker para fallos persistentes (opcional)

## 📝 Notas Importantes

- **No se reintenta para errores de cuota (429)** porque reintentarlo solo empeora el problema
- **No se reintenta para API Key inválida (403)** porque nunca se va a recuperar
- **Sí se reintenta para errores 500** porque son temporales del servidor de Google
- El **timeout total** puede ser hasta `TIMEOUT * MAX_RETRIES + delays` (~3 minutos máximo)
