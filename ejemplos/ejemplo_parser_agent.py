"""
Ejemplo de uso del Parser Agent
Demuestra cómo convertir pseudocódigo a AST custom
"""
from app.modules.parser.service import get_parser_agent
import json


def ejemplo_basico():
    """Ejemplo 1: Parsing básico de procedimiento"""
    print("=" * 60)
    print("EJEMPLO 1: Procedimiento simple")
    print("=" * 60)
    
    code = """
    procedimiento suma(a, b)
        resultado 🡨 a + b
        retornar resultado
    finprocedimiento
    """
    
    parser = get_parser_agent()
    ast = parser.parse(code)
    
    print(f"✓ Programa parseado exitosamente")
    print(f"  - Número de funciones: {len(ast.functions)}")
    print(f"  - Nombre función: {ast.functions[0].name}")
    print(f"  - Parámetros: {[p.name for p in ast.functions[0].params]}")
    print(f"  - Sentencias en body: {len(ast.functions[0].body.statements)}")
    print()


def ejemplo_bubble_sort():
    """Ejemplo 2: Bubble sort completo"""
    print("=" * 60)
    print("EJEMPLO 2: Bubble Sort con AST")
    print("=" * 60)
    
    code = """
    procedimiento ordenamientoBurbuja(A, n)
        para i 🡨 1 hasta n - 1 hacer
            para j 🡨 1 hasta n - i hacer
                si A[j] > A[j + 1] entonces
                    temp 🡨 A[j]
                    A[j] 🡨 A[j + 1]
                    A[j + 1] 🡨 temp
                finsi
            finpara
        finpara
    finprocedimiento
    """
    
    parser = get_parser_agent()
    ast = parser.parse(code)
    
    # Analizar estructura
    func = ast.functions[0]
    outer_for = func.body.statements[0]
    inner_for = outer_for.body.statements[0]
    if_stmt = inner_for.body.statements[0]
    
    print(f"✓ Estructura del algoritmo:")
    print(f"  - Función: {func.name}")
    print(f"  - Bucle externo: for {outer_for.var} 🡨 ... hasta ...")
    print(f"  - Bucle interno: for {inner_for.var} 🡨 ... hasta ...")
    print(f"  - Condicional: if con {len(if_stmt.then_block.statements)} sentencias")
    print()


def ejemplo_serializacion():
    """Ejemplo 3: Serialización a JSON"""
    print("=" * 60)
    print("EJEMPLO 3: Serialización del AST a JSON")
    print("=" * 60)
    
    code = """
    procedimiento factorial(n)
        si n ≤ 1 entonces
            retornar 1
        sino
            retornar n * factorial(n - 1)
        finsi
    finprocedimiento
    """
    
    parser = get_parser_agent()
    ast = parser.parse(code)
    
    # Serializar a diccionario
    ast_dict = ast.to_dict()
    
    # Convertir a JSON
    json_str = json.dumps(ast_dict, indent=2, ensure_ascii=False)
    
    print("✓ AST serializado a JSON:")
    print(json_str[:500])  # Primeros 500 caracteres
    print("...")
    print(f"\n  Total de caracteres JSON: {len(json_str)}")
    print()


def ejemplo_comparacion_con_parse_tree():
    """Ejemplo 4: Diferencia entre Parse Tree y AST"""
    print("=" * 60)
    print("EJEMPLO 4: Parse Tree vs AST Custom")
    print("=" * 60)
    
    code = """
    procedimiento busqueda(arr, n, x)
        para i 🡨 1 hasta n hacer
            si arr[i] = x entonces
                retornar i
            finsi
        finpara
        retornar 0
    finprocedimiento
    """
    
    # Parse a AST custom
    parser = get_parser_agent()
    ast = parser.parse(code)
    
    # Contar nodos en AST
    def count_ast_nodes(obj):
        if hasattr(obj, '__dict__'):
            count = 1
            for value in obj.__dict__.values():
                if isinstance(value, list):
                    count += sum(count_ast_nodes(item) for item in value)
                elif hasattr(value, '__dict__'):
                    count += count_ast_nodes(value)
            return count
        return 0
    
    num_ast_nodes = count_ast_nodes(ast)
    
    # Parse tree tendría ~60+ nodos (con tokens intermedios)
    # AST custom tiene solo nodos semánticos
    
    print(f"✓ Nodos en AST custom: ~{num_ast_nodes}")
    print(f"  Parse tree de Lark tendría: ~60+ nodos (tokens + reglas)")
    print(f"\n  Ventajas del AST custom:")
    print(f"  - Solo nodos semánticos relevantes")
    print(f"  - Tipos fuertemente tipados (Function, For, If, etc.)")
    print(f"  - Fácil de analizar y transformar")
    print(f"  - Serializable a JSON")
    print()


def ejemplo_langgraph():
    """Ejemplo 5: Uso en LangGraph"""
    print("=" * 60)
    print("EJEMPLO 5: Interfaz LangGraph")
    print("=" * 60)
    
    code = """
    procedimiento suma(a, b)
        retornar a + b
    finprocedimiento
    """
    
    parser = get_parser_agent()
    
    # Llamar con interfaz LangGraph
    input_data = {"pseudocode": code}
    result = parser(input_data)
    
    print(f"✓ Resultado LangGraph:")
    print(f"  - success: {result['success']}")
    print(f"  - ast: {type(result['ast'])}")
    print(f"  - error: {result['error']}")
    
    if result['success']:
        ast = result['ast']
        print(f"\n  Función parseada: {ast.functions[0].name}")
    print()


def ejemplo_error():
    """Ejemplo 6: Manejo de errores"""
    print("=" * 60)
    print("EJEMPLO 6: Manejo de errores de sintaxis")
    print("=" * 60)
    
    code = """
    procedimiento invalido(
        x 🡨 1
    # Falta finprocedimiento
    """
    
    parser = get_parser_agent()
    result = parser({"pseudocode": code})
    
    print(f"✓ Error capturado correctamente:")
    print(f"  - success: {result['success']}")
    print(f"  - error: {result['error'][:100]}...")
    print()


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "PARSER AGENT - EJEMPLOS" + " " * 20 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    ejemplos = [
        ejemplo_basico,
        ejemplo_bubble_sort,
        ejemplo_serializacion,
        ejemplo_comparacion_con_parse_tree,
        ejemplo_langgraph,
        ejemplo_error
    ]
    
    for ejemplo in ejemplos:
        try:
            ejemplo()
        except Exception as e:
            print(f"✗ Error en {ejemplo.__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    print("=" * 60)
    print("FIN DE LOS EJEMPLOS")
    print("=" * 60)
