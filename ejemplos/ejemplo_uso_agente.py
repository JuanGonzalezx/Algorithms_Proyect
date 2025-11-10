"""
EJEMPLO COMPLETO DE USO DEL AGENTE SYNTAX_VALIDATOR
====================================================

Este script muestra diferentes formas de usar el agente de validación sintáctica.
"""

from app.shared.models import PseudocodeIn, SyntaxValidationResult
from app.modules.syntax_validator.agent import get_syntax_validator


def ejemplo_1_basico():
    """Ejemplo 1: Uso básico - Validar código correcto"""
    print("\n" + "="*70)
    print("EJEMPLO 1: USO BÁSICO - Código Válido")
    print("="*70)
    
    # Obtener instancia del agente (Singleton)
    validator = get_syntax_validator()
    
    # Código a validar
    codigo = """
procedimiento Suma(a, b)
begin
    resultado 🡨 a + b
    return resultado
end
"""
    
    # Crear input
    input_data = PseudocodeIn(
        text=codigo,
        language_hint="es"  # español
    )
    
    # Validar
    resultado = validator.validate(input_data)
    
    # Mostrar resultados
    print(f"\n📝 Código analizado:")
    print(codigo)
    
    print(f"\n✅ ¿Es válido?: {resultado.era_algoritmo_valido}")
    print(f"📊 Total de errores: {len(resultado.errores)}")
    print(f"🔧 Normalizaciones: {len(resultado.normalizaciones)}")
    
    if resultado.normalizaciones:
        print("\nNormalizaciones aplicadas:")
        for i, norm in enumerate(resultado.normalizaciones, 1):
            print(f"  {i}. {norm}")
    
    print(f"\n💡 Metadata:")
    for key, value in resultado.hints.items():
        print(f"  - {key}: {value}")


def ejemplo_2_con_errores():
    """Ejemplo 2: Detectar errores sintácticos"""
    print("\n" + "="*70)
    print("EJEMPLO 2: DETECCIÓN DE ERRORES")
    print("="*70)
    
    validator = get_syntax_validator()
    
    # Código con error (falta 'end' final)
    codigo_erroneo = """
procedimiento Division(a, b)
begin
    if b ≠ 0 then
    begin
        resultado 🡨 a / b
    end
"""  # ⚠️ Falta 'end' del procedimiento
    
    input_data = PseudocodeIn(text=codigo_erroneo)
    resultado = validator.validate(input_data)
    
    print(f"\n📝 Código analizado:")
    print(codigo_erroneo)
    
    print(f"\n❌ ¿Es válido?: {resultado.era_algoritmo_valido}")
    print(f"🐛 Errores encontrados: {len(resultado.errores)}")
    
    # Mostrar detalles de cada error
    for i, error in enumerate(resultado.errores, 1):
        print(f"\n  Error #{i}:")
        print(f"    📍 Línea: {error.linea}, Columna: {error.columna}")
        print(f"    📋 Regla: {error.regla}")
        print(f"    💬 Detalle: {error.detalle[:80]}...")
        print(f"    💡 Sugerencia: {error.sugerencia}")


def ejemplo_3_normalizaciones():
    """Ejemplo 3: Ver normalizaciones automáticas"""
    print("\n" + "="*70)
    print("EJEMPLO 3: NORMALIZACIONES AUTOMÁTICAS")
    print("="*70)
    
    validator = get_syntax_validator()
    
    # Código con operadores que necesitan normalización
    codigo_a_normalizar = """procedimiento Comparar(x, y)
begin
    if x <= y then
    begin
        mayor 🡨 y
    end
    if x >= y then  
    begin
        mayor 🡨 x
    end
    if x != y then
    begin
        return mayor
    end
end"""  # Sin nueva línea al final, con espacios extras
    
    print(f"\n📝 Código ORIGINAL:")
    print(codigo_a_normalizar)
    print(f"\nCaracteres: {len(codigo_a_normalizar)}")
    
    input_data = PseudocodeIn(text=codigo_a_normalizar)
    resultado = validator.validate(input_data)
    
    print(f"\n🔧 Normalizaciones aplicadas: {len(resultado.normalizaciones)}")
    for i, norm in enumerate(resultado.normalizaciones, 1):
        print(f"  {i}. {norm}")
    
    print(f"\n📝 Código NORMALIZADO:")
    print(resultado.codigo_corregido)
    print(f"\nCaracteres: {len(resultado.codigo_corregido)}")
    
    print(f"\n✅ ¿Es válido?: {resultado.era_algoritmo_valido}")


def ejemplo_4_burbuja():
    """Ejemplo 4: Algoritmo complejo (Burbuja)"""
    print("\n" + "="*70)
    print("EJEMPLO 4: ALGORITMO COMPLEJO - Ordenamiento Burbuja")
    print("="*70)
    
    validator = get_syntax_validator()
    
    # Algoritmo de ordenamiento burbuja completo
    algoritmo_burbuja = """
procedimiento OrdenamientoBurbuja(A[1..n])
begin
    ► Ordenar array usando método de burbuja
    i, j, temp
    
    for i 🡨 1 to n-1 do
    begin
        for j 🡨 1 to n-i do
        begin
            if A[j] > A[j+1] then
            begin
                ► Intercambiar elementos
                temp 🡨 A[j]
                A[j] 🡨 A[j+1]
                A[j+1] 🡨 temp
            end
        end
    end
end
"""
    
    print(f"\n📝 Algoritmo:")
    print(algoritmo_burbuja)
    
    input_data = PseudocodeIn(text=algoritmo_burbuja)
    resultado = validator.validate(input_data)
    
    print(f"\n✅ Validación: {'EXITOSA ✓' if resultado.era_algoritmo_valido else 'FALLIDA ✗'}")
    print(f"📊 Estadísticas:")
    print(f"  - Nodos del AST: {resultado.hints.get('parse_tree_nodes', 'N/A')}")
    print(f"  - Líneas de código: {resultado.hints.get('line_count', 'N/A')}")
    print(f"  - Longitud: {resultado.hints.get('code_length', 'N/A')} caracteres")
    print(f"  - Motor: {resultado.hints.get('parser_engine', 'N/A')}")


def ejemplo_5_multiples_procedimientos():
    """Ejemplo 5: Múltiples procedimientos"""
    print("\n" + "="*70)
    print("EJEMPLO 5: MÚLTIPLES PROCEDIMIENTOS")
    print("="*70)
    
    validator = get_syntax_validator()
    
    codigo_multi = """
procedimiento Factorial(n)
begin
    if n ≤ 1 then
    begin
        return 1
    end
    else
    begin
        return n * Factorial(n-1)
    end
end

procedimiento Main()
begin
    x 🡨 5
    resultado 🡨 Factorial(x)
    return resultado
end
"""
    
    print(f"\n📝 Código con múltiples procedimientos:")
    print(codigo_multi)
    
    input_data = PseudocodeIn(text=codigo_multi)
    resultado = validator.validate(input_data)
    
    print(f"\n✅ ¿Es válido?: {resultado.era_algoritmo_valido}")
    print(f"🔧 Normalizaciones: {len(resultado.normalizaciones)}")
    print(f"🐛 Errores: {len(resultado.errores)}")


def ejemplo_6_uso_en_condicional():
    """Ejemplo 6: Usar el resultado en lógica de negocio"""
    print("\n" + "="*70)
    print("EJEMPLO 6: USO EN LÓGICA DE NEGOCIO")
    print("="*70)
    
    validator = get_syntax_validator()
    
    # Simular recibir código de un usuario
    codigos_usuario = [
        "x 🡨 5",
        "procedimiento Test() begin x 🡨 1 end",
        "for i 🡨 1 to 10 do begin",  # Error: falta end
    ]
    
    print("\n🔍 Procesando códigos de usuarios...\n")
    
    for idx, codigo in enumerate(codigos_usuario, 1):
        print(f"{'─'*70}")
        print(f"Usuario #{idx}:")
        print(f"  Código: {codigo[:50]}{'...' if len(codigo) > 50 else ''}")
        
        input_data = PseudocodeIn(text=codigo)
        resultado = validator.validate(input_data)
        
        if resultado.era_algoritmo_valido:
            print(f"  ✅ Estado: ACEPTADO")
            print(f"  💾 Acción: Guardar en base de datos")
        else:
            print(f"  ❌ Estado: RECHAZADO")
            print(f"  🚫 Acción: Notificar usuario")
            print(f"  📝 Errores: {len(resultado.errores)}")
            if resultado.errores:
                print(f"  💡 Sugerencia: {resultado.errores[0].sugerencia}")


def ejemplo_7_preparacion_langgraph():
    """Ejemplo 7: Preparación para usar con LangGraph"""
    print("\n" + "="*70)
    print("EJEMPLO 7: PREPARACIÓN PARA LANGGRAPH")
    print("="*70)
    
    validator = get_syntax_validator()
    
    # Simular un estado de grafo
    estado_inicial = {
        "text": "procedimiento Test(n)\nbegin\n    x 🡨 n + 1\nend",
        "language_hint": "es",
        "usuario_id": "user123",
        "timestamp": "2025-11-09"
    }
    
    print("\n📊 Estado inicial del grafo:")
    for key, value in estado_inicial.items():
        if key == "text":
            print(f"  {key}: {value[:30]}...")
        else:
            print(f"  {key}: {value}")
    
    # Usar el método __call__ (interfaz LangGraph)
    print("\n🔄 Procesando con método __call__...")
    estado_actualizado = validator({"input": PseudocodeIn(**{k: v for k, v in estado_inicial.items() if k in ["text", "language_hint"]})})
    
    print("\n📊 Estado actualizado:")
    print(f"  era_algoritmo_valido: {estado_actualizado.get('era_algoritmo_valido')}")
    print(f"  errores_sintaxis: {len(estado_actualizado.get('errores_sintaxis', []))}")
    print(f"  normalizaciones: {len(estado_actualizado.get('normalizaciones', []))}")
    print(f"  codigo_corregido: {estado_actualizado.get('codigo_corregido', '')[:50]}...")


def ejemplo_8_manejo_excepciones():
    """Ejemplo 8: Manejo robusto de errores"""
    print("\n" + "="*70)
    print("EJEMPLO 8: MANEJO DE EXCEPCIONES")
    print("="*70)
    
    validator = get_syntax_validator()
    
    casos_especiales = [
        ("Código vacío", ""),
        ("Solo espacios", "   \n\n   "),
        ("Comentario solo", "► Esto es un comentario"),
        ("Código muy largo", "x 🡨 1\n" * 100),
    ]
    
    for nombre, codigo in casos_especiales:
        print(f"\n{'─'*70}")
        print(f"Caso: {nombre}")
        print(f"Longitud: {len(codigo)} caracteres")
        
        try:
            input_data = PseudocodeIn(text=codigo)
            resultado = validator.validate(input_data)
            
            print(f"✅ Procesado exitosamente")
            print(f"   Válido: {resultado.era_algoritmo_valido}")
            print(f"   Errores: {len(resultado.errores)}")
            
        except Exception as e:
            print(f"❌ Error capturado: {type(e).__name__}")
            print(f"   Mensaje: {str(e)[:80]}")


def main():
    """Ejecutar todos los ejemplos"""
    print("\n" + "🎯"*35)
    print("EJEMPLOS DE USO DEL AGENTE SYNTAX_VALIDATOR")
    print("🎯"*35)
    
    try:
        ejemplo_1_basico()
        ejemplo_2_con_errores()
        ejemplo_3_normalizaciones()
        ejemplo_4_burbuja()
        ejemplo_5_multiples_procedimientos()
        ejemplo_6_uso_en_condicional()
        ejemplo_7_preparacion_langgraph()
        ejemplo_8_manejo_excepciones()
        
        print("\n" + "="*70)
        print("✅ TODOS LOS EJEMPLOS EJECUTADOS EXITOSAMENTE")
        print("="*70)
        print("\n💡 Próximos pasos:")
        print("  1. Integrar con tu flujo de trabajo")
        print("  2. Añadir más validaciones personalizadas")
        print("  3. Conectar con el siguiente agente (semantic_analyzer)")
        print("  4. Crear un grafo LangGraph completo")
        print()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
