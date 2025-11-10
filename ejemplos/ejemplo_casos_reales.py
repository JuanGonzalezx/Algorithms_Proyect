"""
EJEMPLO PRÁCTICO: Cómo usar el agente en TU aplicación
======================================================

Este ejemplo muestra casos de uso reales que puedes implementar en tu proyecto.
"""

from app.shared.models import PseudocodeIn, SyntaxValidationResult
from app.modules.syntax_validator.agent import get_syntax_validator


# ============================================================================
# CASO 1: Validar código antes de guardarlo en la base de datos
# ============================================================================
def validar_antes_de_guardar(codigo_usuario: str, usuario_id: str) -> dict:
    """
    Valida el código del usuario antes de guardarlo en BD.
    
    Returns:
        dict con información sobre si se puede guardar o no
    """
    print("\n" + "🔍 CASO 1: Validar antes de guardar en BD")
    print("="*60)
    
    validator = get_syntax_validator()
    
    # Validar
    resultado = validator.validate(PseudocodeIn(text=codigo_usuario))
    
    if resultado.era_algoritmo_valido:
        # ✅ Código válido - proceder a guardar
        return {
            "puede_guardar": True,
            "codigo_normalizado": resultado.codigo_corregido,
            "usuario_id": usuario_id,
            "metadata": {
                "lineas": resultado.hints.get('line_count'),
                "normalizaciones": resultado.normalizaciones,
                "complejidad_estimada": "O(?)"  # Pendiente del siguiente agente
            }
        }
    else:
        # ❌ Código inválido - rechazar
        errores_detalle = [
            {
                "linea": e.linea,
                "mensaje": e.detalle[:100],
                "sugerencia": e.sugerencia
            }
            for e in resultado.errores
        ]
        
        return {
            "puede_guardar": False,
            "errores": errores_detalle,
            "usuario_id": usuario_id
        }


# ============================================================================
# CASO 2: Endpoint de FastAPI que usa el agente
# ============================================================================
async def endpoint_analizar_algoritmo(codigo: str, usuario: str):
    """
    Simulación de un endpoint que analiza un algoritmo.
    En tu app/api/routes.py podrías tener algo así.
    """
    print("\n" + "🌐 CASO 2: Endpoint FastAPI")
    print("="*60)
    
    validator = get_syntax_validator()
    
    try:
        # Validar sintaxis
        resultado = validator.validate(PseudocodeIn(text=codigo))
        
        if not resultado.era_algoritmo_valido:
            # Retornar error 400 con detalles
            return {
                "status": "error",
                "code": 400,
                "message": "Código con errores sintácticos",
                "errors": [
                    {
                        "line": e.linea,
                        "column": e.columna,
                        "suggestion": e.sugerencia
                    }
                    for e in resultado.errores
                ]
            }
        
        # ✅ Sintaxis válida - continuar con análisis
        return {
            "status": "success",
            "code": 200,
            "data": {
                "sintaxis_valida": True,
                "codigo_normalizado": resultado.codigo_corregido,
                "normalizaciones_aplicadas": resultado.normalizaciones,
                "estadisticas": {
                    "lineas": resultado.hints.get('line_count'),
                    "caracteres": resultado.hints.get('code_length'),
                    "nodos_ast": resultado.hints.get('parse_tree_nodes')
                },
                # Aquí llamarías al siguiente agente (semantic_analyzer)
                "siguiente_paso": "analisis_semantico"
            }
        }
        
    except Exception as e:
        # Error interno
        return {
            "status": "error",
            "code": 500,
            "message": f"Error interno: {str(e)}"
        }


# ============================================================================
# CASO 3: Pipeline de validación en cadena
# ============================================================================
def pipeline_validacion(codigo: str) -> dict:
    """
    Pipeline que valida el código en múltiples pasos.
    Prepara para usar con LangGraph.
    """
    print("\n" + "🔄 CASO 3: Pipeline de validación")
    print("="*60)
    
    pipeline_state = {
        "codigo_original": codigo,
        "pasos_completados": [],
        "errores_acumulados": [],
        "puede_continuar": True
    }
    
    # PASO 1: Validación sintáctica
    validator = get_syntax_validator()
    resultado_sintaxis = validator.validate(PseudocodeIn(text=codigo))
    
    pipeline_state["pasos_completados"].append("sintaxis")
    pipeline_state["sintaxis"] = {
        "valido": resultado_sintaxis.era_algoritmo_valido,
        "errores": len(resultado_sintaxis.errores),
        "normalizaciones": len(resultado_sintaxis.normalizaciones)
    }
    
    if not resultado_sintaxis.era_algoritmo_valido:
        pipeline_state["puede_continuar"] = False
        pipeline_state["errores_acumulados"].extend(resultado_sintaxis.errores)
        pipeline_state["mensaje"] = "❌ Pipeline detenido: Errores de sintaxis"
        return pipeline_state
    
    # Actualizar código para siguiente paso
    pipeline_state["codigo_procesado"] = resultado_sintaxis.codigo_corregido
    
    # PASO 2: Validación semántica (futuro)
    # semantic_analyzer = get_semantic_analyzer()
    # resultado_semantica = semantic_analyzer.validate(...)
    pipeline_state["mensaje"] = "✅ Sintaxis válida - Listo para análisis semántico"
    
    # PASO 3: Cálculo de complejidad (futuro)
    # complexity_calculator = get_complexity_calculator()
    # resultado_complejidad = complexity_calculator.calculate(...)
    
    return pipeline_state


# ============================================================================
# CASO 4: Integración con un sistema de calificación automática
# ============================================================================
def calificar_tarea_estudiante(codigo_estudiante: str, nombre_estudiante: str) -> dict:
    """
    Sistema de calificación automática para ejercicios de algoritmos.
    """
    print("\n" + "🎓 CASO 4: Sistema de calificación")
    print("="*60)
    
    validator = get_syntax_validator()
    resultado = validator.validate(PseudocodeIn(text=codigo_estudiante))
    
    calificacion = {
        "estudiante": nombre_estudiante,
        "puntos_sintaxis": 0,
        "puntos_totales": 100,
        "feedback": []
    }
    
    # Criterio 1: Sintaxis correcta (30 puntos)
    if resultado.era_algoritmo_valido:
        calificacion["puntos_sintaxis"] = 30
        calificacion["feedback"].append("✅ Sintaxis correcta (+30 pts)")
    else:
        puntos_perdidos = len(resultado.errores) * 5
        calificacion["puntos_sintaxis"] = max(0, 30 - puntos_perdidos)
        calificacion["feedback"].append(
            f"⚠️ {len(resultado.errores)} errores de sintaxis (-{puntos_perdidos} pts)"
        )
        
        # Agregar feedback específico
        for error in resultado.errores[:3]:  # Máximo 3 errores
            calificacion["feedback"].append(
                f"  - Línea {error.linea}: {error.sugerencia}"
            )
    
    # Criterio 2: Buenas prácticas (bonus)
    if resultado.era_algoritmo_valido:
        lineas = resultado.hints.get('line_count', 0)
        if lineas < 50:
            calificacion["feedback"].append("✨ Código conciso (+5 pts bonus)")
            calificacion["puntos_sintaxis"] += 5
        
        if resultado.normalizaciones:
            calificacion["feedback"].append(
                f"ℹ️ Se aplicaron {len(resultado.normalizaciones)} normalizaciones"
            )
    
    return calificacion


# ============================================================================
# CASO 5: Batch processing - Validar múltiples algoritmos
# ============================================================================
def procesar_lote_algoritmos(algoritmos: list[dict]) -> list[dict]:
    """
    Procesa un lote de algoritmos en paralelo (conceptualmente).
    Útil para validar múltiples submissions a la vez.
    """
    print("\n" + "📦 CASO 5: Procesamiento por lotes")
    print("="*60)
    
    validator = get_syntax_validator()
    resultados = []
    
    for item in algoritmos:
        resultado = validator.validate(PseudocodeIn(text=item["codigo"]))
        
        resultados.append({
            "id": item["id"],
            "nombre": item.get("nombre", "Sin nombre"),
            "valido": resultado.era_algoritmo_valido,
            "errores": len(resultado.errores),
            "lineas": resultado.hints.get('line_count', 0),
            "procesado_en": "2025-11-09"
        })
    
    return resultados


# ============================================================================
# CASO 6: Integración con frontend (respuesta JSON amigable)
# ============================================================================
def formatear_para_frontend(codigo: str) -> dict:
    """
    Formatea la respuesta del agente para consumo fácil del frontend.
    """
    print("\n" + "💻 CASO 6: Respuesta para frontend")
    print("="*60)
    
    validator = get_syntax_validator()
    resultado = validator.validate(PseudocodeIn(text=codigo))
    
    # Formato amigable para frontend
    respuesta = {
        "validacion": {
            "estado": "valido" if resultado.era_algoritmo_valido else "invalido",
            "mensaje": "✅ Código sintácticamente correcto" if resultado.era_algoritmo_valido 
                      else "❌ Se encontraron errores de sintaxis",
            "icono": "✅" if resultado.era_algoritmo_valido else "❌"
        },
        "errores": [
            {
                "tipo": "sintaxis",
                "gravedad": "error",
                "posicion": {
                    "linea": e.linea,
                    "columna": e.columna
                },
                "mensaje": e.detalle if e.detalle else "Error de sintaxis",
                "sugerencia": e.sugerencia,
                "codigo_error": f"SYN{idx:03d}"
            }
            for idx, e in enumerate(resultado.errores, 1)
        ],
        "informacion": {
            "codigo_normalizado": resultado.codigo_corregido,
            "cambios_aplicados": resultado.normalizaciones,
            "estadisticas": {
                "lineas": resultado.hints.get('line_count'),
                "caracteres": resultado.hints.get('code_length'),
                "complejidad_ast": resultado.hints.get('parse_tree_nodes')
            }
        },
        "acciones_sugeridas": [
            "Corregir errores de sintaxis" if not resultado.era_algoritmo_valido 
            else "Proceder con análisis de complejidad",
            "Revisar las normalizaciones aplicadas" if resultado.normalizaciones 
            else None
        ]
    }
    
    # Limpiar None values
    respuesta["acciones_sugeridas"] = [
        a for a in respuesta["acciones_sugeridas"] if a is not None
    ]
    
    return respuesta


# ============================================================================
# EJECUTAR TODOS LOS CASOS
# ============================================================================
if __name__ == "__main__":
    print("\n" + "🎯"*30)
    print("CASOS DE USO PRÁCTICOS DEL AGENTE")
    print("🎯"*30)
    
    # CASO 1
    codigo_usuario = """
procedimiento BusquedaBinaria(A[1..n], valor)
begin
    inicio 🡨 1
    fin 🡨 n
    
    while inicio ≤ fin do
    begin
        medio 🡨 └(inicio + fin) / 2┘
        
        if A[medio] = valor then
        begin
            return medio
        end
        else
        begin
            if A[medio] < valor then
            begin
                inicio 🡨 medio + 1
            end
            else
            begin
                fin 🡨 medio - 1
            end
        end
    end
    
    return -1
end
"""
    
    resultado1 = validar_antes_de_guardar(codigo_usuario, "user_123")
    print(f"\n✅ ¿Puede guardar?: {resultado1['puede_guardar']}")
    if resultado1['puede_guardar']:
        print(f"📊 Líneas: {resultado1['metadata']['lineas']}")
        print(f"🔧 Normalizaciones: {len(resultado1['metadata']['normalizaciones'])}")
    
    # CASO 2
    import asyncio
    resultado2 = asyncio.run(endpoint_analizar_algoritmo(codigo_usuario, "juan"))
    print(f"\n📡 Status: {resultado2['status']}")
    print(f"🔢 Code: {resultado2['code']}")
    
    # CASO 3
    resultado3 = pipeline_validacion(codigo_usuario)
    print(f"\n🔄 Pasos completados: {resultado3['pasos_completados']}")
    print(f"📝 Mensaje: {resultado3['mensaje']}")
    print(f"✅ Puede continuar: {resultado3['puede_continuar']}")
    
    # CASO 4
    codigo_estudiante = "for i 🡨 1 to 10 do begin x 🡨 x + 1 end"
    resultado4 = calificar_tarea_estudiante(codigo_estudiante, "María García")
    print(f"\n🎓 Estudiante: {resultado4['estudiante']}")
    print(f"📊 Puntos: {resultado4['puntos_sintaxis']}/{resultado4['puntos_totales']}")
    print(f"📝 Feedback:")
    for feedback in resultado4['feedback']:
        print(f"   {feedback}")
    
    # CASO 5
    lote = [
        {"id": 1, "nombre": "Burbuja", "codigo": "x 🡨 5"},
        {"id": 2, "nombre": "Selección", "codigo": "y 🡨 10"},
        {"id": 3, "nombre": "Inserción", "codigo": "for i 🡨 1 to n do begin"},
    ]
    resultado5 = procesar_lote_algoritmos(lote)
    print(f"\n📦 Procesados: {len(resultado5)} algoritmos")
    for r in resultado5:
        print(f"   #{r['id']} {r['nombre']}: {'✅' if r['valido'] else '❌'} ({r['errores']} errores)")
    
    # CASO 6
    resultado6 = formatear_para_frontend(codigo_usuario)
    print(f"\n💻 Frontend Response:")
    print(f"   Estado: {resultado6['validacion']['estado']}")
    print(f"   Mensaje: {resultado6['validacion']['mensaje']}")
    print(f"   Errores: {len(resultado6['errores'])}")
    print(f"   Acciones: {resultado6['acciones_sugeridas']}")
    
    print("\n" + "="*60)
    print("✅ TODOS LOS CASOS EJECUTADOS")
    print("="*60)
    print("\n💡 Estos son ejemplos reales de cómo usar el agente en tu app!")
    print()
