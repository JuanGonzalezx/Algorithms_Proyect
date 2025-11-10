"""
Script de prueba para el parser de pseudocódigo
Ejecuta ejemplos directos sin necesidad del servidor
"""
from app.core.psc_parser import PseudocodeParser
import json


def test_example(name: str, code: str):
    """Prueba un ejemplo de pseudocódigo"""
    print(f"\n{'='*60}")
    print(f"📝 {name}")
    print(f"{'='*60}")
    print(f"Código:\n{code}")
    
    try:
        parser = PseudocodeParser()
        program = parser.build(code)
        
        print(f"\n✅ ¡Parsing exitoso!")
        print(f"Funciones encontradas: {len(program.functions)}")
        
        if program.functions:
            func = program.functions[0]
            print(f"Nombre: {func.name}")
            print(f"Parámetros: {[p.name for p in func.params]}")
            print(f"Statements en body: {len(func.body.statements)}")
            
        print(f"\n🌳 AST en JSON:")
        print(json.dumps(program.to_dict(), indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🧪 PROBANDO PARSER DE PSEUDOCÓDIGO")
    print("="*60)
    
    # Ejemplo 1: Suma simple
    test_example(
        "Ejemplo 1: Suma Simple",
        """
procedimiento suma(a, b)
begin
    return a + b
end
        """
    )
    
    # Ejemplo 2: Suma de array con for
    test_example(
        "Ejemplo 2: Suma de Array",
        """
procedimiento suma_array(arr, n)
begin
    suma 🡨 0
    for i 🡨 0 to n - 1 do
    begin
        suma 🡨 suma + arr[i]
    end
    return suma
end
        """
    )
    
    # Ejemplo 3: Factorial con if-else
    test_example(
        "Ejemplo 3: Factorial Recursivo",
        """
procedimiento factorial(n)
begin
    if n ≤ 1 then
    begin
        return 1
    end
    else
    begin
        return n * factorial(n - 1)
    end
end
        """
    )
    
    # Ejemplo 4: Búsqueda binaria
    test_example(
        "Ejemplo 4: Búsqueda Binaria",
        """
procedimiento buscar(arr, objetivo, n)
begin
    izq 🡨 0
    der 🡨 n - 1
    while izq ≤ der do
    begin
        medio 🡨 (izq + der) / 2
        if arr[medio] = objetivo then
        begin
            return medio
        end
        if arr[medio] < objetivo then
        begin
            izq 🡨 medio + 1
        end
        else
        begin
            der 🡨 medio - 1
        end
    end
    return -1
end
        """
    )
    
    # Ejemplo 5: Matriz (acceso multi-dimensional)
    test_example(
        "Ejemplo 5: Suma de Matriz",
        """
procedimiento suma_matriz(matriz, filas, cols)
begin
    suma 🡨 0
    for i 🡨 0 to filas - 1 do
    begin
        for j 🡨 0 to cols - 1 do
        begin
            suma 🡨 suma + matriz[i][j]
        end
    end
    return suma
end
        """
    )
    
    print(f"\n{'='*60}")
    print("✅ ¡TODAS LAS PRUEBAS COMPLETADAS!")
    print("="*60)
