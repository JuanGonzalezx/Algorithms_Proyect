"""
Script de prueba para el agente de validación sintáctica.
"""
from app.shared.models import PseudocodeIn, SyntaxValidationResult
from app.modules.syntax_validator.agent import get_syntax_validator


def test_valid_pseudocode():
    """Prueba con pseudocódigo válido."""
    print("\n" + "="*60)
    print("TEST 1: Pseudocódigo válido")
    print("="*60)
    
    code = """
procedimiento OrdenarBurbuja(A[1..n])
begin
    i, j, temp
    for i 🡨 1 to n-1 do
    begin
        for j 🡨 1 to n-i do
        begin
            if A[j] > A[j+1] then
            begin
                temp 🡨 A[j]
                A[j] 🡨 A[j+1]
                A[j+1] 🡨 temp
            end
        end
    end
end
"""
    
    validator = get_syntax_validator()
    input_data = PseudocodeIn(text=code, language_hint="es")
    result = validator.validate(input_data)
    
    print(f"✓ Válido: {result.era_algoritmo_valido}")
    print(f"✓ Errores: {len(result.errores)}")
    print(f"✓ Normalizaciones: {len(result.normalizaciones)}")
    if result.normalizaciones:
        for norm in result.normalizaciones:
            print(f"  - {norm}")
    print(f"✓ Hints: {result.hints}")


def test_invalid_pseudocode():
    """Prueba con pseudocódigo inválido."""
    print("\n" + "="*60)
    print("TEST 2: Pseudocódigo con errores de sintaxis")
    print("="*60)
    
    # Falta 'end' al final
    code = """
procedimiento Ejemplo(n)
begin
    x 🡨 5
    if x > 0 then
    begin
        x 🡨 x + 1
    end
"""
    
    validator = get_syntax_validator()
    input_data = PseudocodeIn(text=code, language_hint="es")
    result = validator.validate(input_data)
    
    print(f"✓ Válido: {result.era_algoritmo_valido}")
    print(f"✓ Errores encontrados: {len(result.errores)}")
    for i, error in enumerate(result.errores, 1):
        print(f"\n  Error {i}:")
        print(f"    Línea: {error.linea}")
        print(f"    Columna: {error.columna}")
        print(f"    Regla: {error.regla}")
        print(f"    Detalle: {error.detalle[:100]}...")
        print(f"    Sugerencia: {error.sugerencia}")


def test_normalization():
    """Prueba de normalizaciones."""
    print("\n" + "="*60)
    print("TEST 3: Normalizaciones de código")
    print("="*60)
    
    # Código con símbolos que necesitan normalización
    code = """procedimiento Test(n)
begin
    x 🡨 5
    if x <= 10 then
    begin
        y 🡨 x + 1
    end
end"""
    
    validator = get_syntax_validator()
    input_data = PseudocodeIn(text=code, language_hint="es")
    result = validator.validate(input_data)
    
    print(f"✓ Válido: {result.era_algoritmo_valido}")
    print(f"✓ Normalizaciones aplicadas: {len(result.normalizaciones)}")
    for norm in result.normalizaciones:
        print(f"  - {norm}")
    
    print("\n✓ Código normalizado:")
    print(result.codigo_corregido)


def test_simple_assignment():
    """Prueba con asignación simple."""
    print("\n" + "="*60)
    print("TEST 4: Asignación simple")
    print("="*60)
    
    code = """
x 🡨 5
"""
    
    validator = get_syntax_validator()
    input_data = PseudocodeIn(text=code, language_hint="es")
    result = validator.validate(input_data)
    
    print(f"✓ Válido: {result.era_algoritmo_valido}")
    print(f"✓ Errores: {len(result.errores)}")
    if result.errores:
        for error in result.errores:
            print(f"  Error: {error.detalle}")


if __name__ == "__main__":
    print("\n" + "🧪 PRUEBAS DEL AGENTE DE VALIDACIÓN SINTÁCTICA " + "🧪")
    
    try:
        test_valid_pseudocode()
        test_invalid_pseudocode()
        test_normalization()
        test_simple_assignment()
        
        print("\n" + "="*60)
        print("✅ TODAS LAS PRUEBAS COMPLETADAS")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
