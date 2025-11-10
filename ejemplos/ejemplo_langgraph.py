"""
EJEMPLO AVANZADO: Integración con LangGraph
===========================================

Este ejemplo muestra cómo crear un grafo de agentes usando LangGraph
con el agente syntax_validator como primer nodo.
"""

from typing import TypedDict, List, Optional, Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
import operator

from app.shared.models import PseudocodeIn, ErrorItem
from app.modules.syntax_validator.agent import get_syntax_validator


# ============================================================================
# DEFINIR EL ESTADO DEL GRAFO
# ============================================================================
class AlgorithmAnalysisState(TypedDict):
    """
    Estado compartido entre todos los agentes del grafo.
    Cada agente puede leer y escribir en este estado.
    """
    # Input inicial
    pseudocode_text: str
    language_hint: str
    user_id: Optional[str]
    
    # Estado de validación sintáctica
    syntax_valid: bool
    syntax_errors: List[dict]
    normalized_code: str
    normalizations: List[str]
    
    # Estado de análisis semántico (futuro)
    semantic_valid: Optional[bool]
    variables_declared: Optional[List[str]]
    
    # Estado de cálculo de complejidad (futuro)
    time_complexity: Optional[str]
    space_complexity: Optional[str]
    complexity_case: Optional[str]  # best, avg, worst
    
    # Estado de optimización (futuro)
    optimization_suggestions: Optional[List[str]]
    
    # Metadatos
    current_step: str
    errors_accumulated: Annotated[List[dict], operator.add]  # Se acumulan
    completed_steps: Annotated[List[str], operator.add]  # Se acumulan
    can_continue: bool


# ============================================================================
# NODO 1: VALIDACIÓN SINTÁCTICA (Ya implementado)
# ============================================================================
def syntax_validation_node(state: AlgorithmAnalysisState) -> AlgorithmAnalysisState:
    """
    Nodo que valida la sintaxis del pseudocódigo.
    """
    print("\n🔍 NODO 1: Validando sintaxis...")
    
    # Obtener el agente
    validator = get_syntax_validator()
    
    # Crear input
    input_data = PseudocodeIn(
        text=state["pseudocode_text"],
        language_hint=state.get("language_hint", "es")
    )
    
    # Validar
    result = validator.validate(input_data)
    
    # Actualizar estado
    updated_state = state.copy()
    updated_state["syntax_valid"] = result.era_algoritmo_valido
    updated_state["normalized_code"] = result.codigo_corregido
    updated_state["normalizations"] = result.normalizaciones
    updated_state["syntax_errors"] = [
        {
            "tipo": "sintaxis",
            "linea": e.linea,
            "columna": e.columna,
            "detalle": e.detalle,
            "sugerencia": e.sugerencia
        }
        for e in result.errores
    ]
    updated_state["current_step"] = "syntax_validation"
    updated_state["completed_steps"] = ["syntax_validation"]
    updated_state["errors_accumulated"] = updated_state["syntax_errors"]
    updated_state["can_continue"] = result.era_algoritmo_valido
    
    print(f"   ✅ Sintaxis válida: {result.era_algoritmo_valido}")
    print(f"   📝 Errores: {len(result.errores)}")
    print(f"   🔧 Normalizaciones: {len(result.normalizaciones)}")
    
    return updated_state


# ============================================================================
# NODO 2: ANÁLISIS SEMÁNTICO (Placeholder - futuro)
# ============================================================================
def semantic_analysis_node(state: AlgorithmAnalysisState) -> AlgorithmAnalysisState:
    """
    Nodo que analiza la semántica del pseudocódigo.
    NOTA: Este es un placeholder para el futuro agente semantic_analyzer.
    """
    print("\n🧠 NODO 2: Analizando semántica...")
    print("   ⚠️ Placeholder - Agente pendiente de implementación")
    
    updated_state = state.copy()
    updated_state["semantic_valid"] = True  # Simular éxito
    updated_state["variables_declared"] = ["i", "j", "temp"]  # Ejemplo
    updated_state["current_step"] = "semantic_analysis"
    updated_state["completed_steps"] = ["semantic_analysis"]
    updated_state["can_continue"] = True
    
    print("   ✅ Análisis semántico: OK (simulado)")
    
    return updated_state


# ============================================================================
# NODO 3: CÁLCULO DE COMPLEJIDAD (Placeholder - futuro)
# ============================================================================
def complexity_calculation_node(state: AlgorithmAnalysisState) -> AlgorithmAnalysisState:
    """
    Nodo que calcula la complejidad temporal y espacial.
    NOTA: Este es un placeholder para el futuro agente complexity_calculator.
    """
    print("\n📊 NODO 3: Calculando complejidad...")
    print("   ⚠️ Placeholder - Agente pendiente de implementación")
    
    updated_state = state.copy()
    updated_state["time_complexity"] = "O(n²)"  # Ejemplo
    updated_state["space_complexity"] = "O(1)"  # Ejemplo
    updated_state["complexity_case"] = "worst"
    updated_state["current_step"] = "complexity_calculation"
    updated_state["completed_steps"] = ["complexity_calculation"]
    updated_state["can_continue"] = True
    
    print("   ✅ Complejidad temporal: O(n²) (simulado)")
    print("   ✅ Complejidad espacial: O(1) (simulado)")
    
    return updated_state


# ============================================================================
# NODO 4: SUGERENCIAS DE OPTIMIZACIÓN (Placeholder - futuro)
# ============================================================================
def optimization_suggestions_node(state: AlgorithmAnalysisState) -> AlgorithmAnalysisState:
    """
    Nodo que sugiere optimizaciones al algoritmo.
    NOTA: Este es un placeholder para el futuro agente optimizer_suggester.
    """
    print("\n💡 NODO 4: Generando sugerencias...")
    print("   ⚠️ Placeholder - Agente pendiente de implementación")
    
    updated_state = state.copy()
    updated_state["optimization_suggestions"] = [
        "Considerar usar QuickSort para mejor complejidad promedio",
        "Agregar validación de entrada",
        "Documentar casos especiales"
    ]
    updated_state["current_step"] = "optimization"
    updated_state["completed_steps"] = ["optimization"]
    
    print("   ✅ Sugerencias generadas: 3 (simulado)")
    
    return updated_state


# ============================================================================
# FUNCIÓN DE DECISIÓN: ¿Continuar o detenerse?
# ============================================================================
def should_continue(state: AlgorithmAnalysisState) -> str:
    """
    Decide si el flujo debe continuar o detenerse.
    """
    if not state["can_continue"]:
        print("\n⚠️ DECISIÓN: Detener flujo (errores encontrados)")
        return "end"
    
    if state["current_step"] == "syntax_validation":
        print("\n✅ DECISIÓN: Continuar a análisis semántico")
        return "semantic"
    elif state["current_step"] == "semantic_analysis":
        print("\n✅ DECISIÓN: Continuar a cálculo de complejidad")
        return "complexity"
    elif state["current_step"] == "complexity_calculation":
        print("\n✅ DECISIÓN: Continuar a optimización")
        return "optimization"
    else:
        print("\n✅ DECISIÓN: Finalizar flujo")
        return "end"


# ============================================================================
# CREAR EL GRAFO DE LANGGRAPH
# ============================================================================
def create_algorithm_analysis_graph():
    """
    Crea y retorna el grafo de análisis de algoritmos.
    """
    # Crear el grafo
    workflow = StateGraph(AlgorithmAnalysisState)
    
    # Añadir nodos
    workflow.add_node("syntax_validation", syntax_validation_node)
    workflow.add_node("semantic_analysis", semantic_analysis_node)
    workflow.add_node("complexity_calculation", complexity_calculation_node)
    workflow.add_node("optimization", optimization_suggestions_node)
    
    # Definir el punto de entrada
    workflow.set_entry_point("syntax_validation")
    
    # Definir edges condicionales
    workflow.add_conditional_edges(
        "syntax_validation",
        should_continue,
        {
            "semantic": "semantic_analysis",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "semantic_analysis",
        should_continue,
        {
            "complexity": "complexity_calculation",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "complexity_calculation",
        should_continue,
        {
            "optimization": "optimization",
            "end": END
        }
    )
    
    workflow.add_edge("optimization", END)
    
    # Compilar el grafo
    app = workflow.compile()
    
    return app


# ============================================================================
# EJEMPLO DE USO
# ============================================================================
def ejemplo_grafo_completo():
    """
    Ejecuta un ejemplo completo del grafo de análisis.
    """
    print("\n" + "🎯"*30)
    print("EJEMPLO: GRAFO COMPLETO DE ANÁLISIS")
    print("🎯"*30)
    
    # Crear el grafo
    app = create_algorithm_analysis_graph()
    
    # Estado inicial
    initial_state = AlgorithmAnalysisState(
        pseudocode_text="""
procedimiento OrdenamientoBurbuja(A[1..n])
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
""",
        language_hint="es",
        user_id="user_123",
        syntax_valid=False,
        syntax_errors=[],
        normalized_code="",
        normalizations=[],
        semantic_valid=None,
        variables_declared=None,
        time_complexity=None,
        space_complexity=None,
        complexity_case=None,
        optimization_suggestions=None,
        current_step="",
        errors_accumulated=[],
        completed_steps=[],
        can_continue=True
    )
    
    print("\n📥 Estado inicial:")
    print(f"   Usuario: {initial_state['user_id']}")
    print(f"   Código: {initial_state['pseudocode_text'][:50]}...")
    
    # Ejecutar el grafo
    print("\n" + "="*70)
    print("🚀 EJECUTANDO GRAFO...")
    print("="*70)
    
    final_state = app.invoke(initial_state)
    
    # Mostrar resultados finales
    print("\n" + "="*70)
    print("📊 RESULTADOS FINALES")
    print("="*70)
    
    print(f"\n✅ Pasos completados: {final_state['completed_steps']}")
    print(f"\n📝 Validación sintáctica:")
    print(f"   Válido: {final_state['syntax_valid']}")
    print(f"   Errores: {len(final_state['syntax_errors'])}")
    print(f"   Normalizaciones: {len(final_state['normalizations'])}")
    
    print(f"\n🧠 Análisis semántico:")
    print(f"   Válido: {final_state['semantic_valid']}")
    print(f"   Variables: {final_state['variables_declared']}")
    
    print(f"\n📊 Complejidad:")
    print(f"   Temporal: {final_state['time_complexity']}")
    print(f"   Espacial: {final_state['space_complexity']}")
    print(f"   Caso: {final_state['complexity_case']}")
    
    print(f"\n💡 Sugerencias:")
    if final_state['optimization_suggestions']:
        for i, sug in enumerate(final_state['optimization_suggestions'], 1):
            print(f"   {i}. {sug}")
    
    print(f"\n📈 Total de errores: {len(final_state['errors_accumulated'])}")
    
    return final_state


def ejemplo_grafo_con_error():
    """
    Ejecuta el grafo con código que tiene errores.
    """
    print("\n" + "🎯"*30)
    print("EJEMPLO: GRAFO CON CÓDIGO ERRÓNEO")
    print("🎯"*30)
    
    app = create_algorithm_analysis_graph()
    
    # Código con error (falta 'end')
    initial_state = AlgorithmAnalysisState(
        pseudocode_text="""
procedimiento Test(n)
begin
    x 🡨 5
    if x > 0 then
    begin
        x 🡨 x + 1
    end
""",  # Falta 'end' del procedimiento
        language_hint="es",
        user_id="user_456",
        syntax_valid=False,
        syntax_errors=[],
        normalized_code="",
        normalizations=[],
        semantic_valid=None,
        variables_declared=None,
        time_complexity=None,
        space_complexity=None,
        complexity_case=None,
        optimization_suggestions=None,
        current_step="",
        errors_accumulated=[],
        completed_steps=[],
        can_continue=True
    )
    
    print("\n📥 Estado inicial:")
    print(f"   Usuario: {initial_state['user_id']}")
    print(f"   Código con error sintáctico")
    
    print("\n" + "="*70)
    print("🚀 EJECUTANDO GRAFO...")
    print("="*70)
    
    final_state = app.invoke(initial_state)
    
    print("\n" + "="*70)
    print("📊 RESULTADOS FINALES")
    print("="*70)
    
    print(f"\n❌ El flujo se detuvo en: {final_state['current_step']}")
    print(f"📝 Pasos completados: {final_state['completed_steps']}")
    print(f"🐛 Errores encontrados: {len(final_state['errors_accumulated'])}")
    
    for i, error in enumerate(final_state['errors_accumulated'], 1):
        print(f"\n   Error {i}:")
        print(f"      Tipo: {error['tipo']}")
        print(f"      Línea: {error['linea']}")
        print(f"      Sugerencia: {error['sugerencia']}")
    
    return final_state


# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    print("\n" + "🌟"*30)
    print("INTEGRACIÓN CON LANGGRAPH")
    print("🌟"*30)
    
    # Ejemplo 1: Flujo completo exitoso
    resultado1 = ejemplo_grafo_completo()
    
    print("\n\n" + "─"*70 + "\n")
    
    # Ejemplo 2: Flujo que se detiene por error
    resultado2 = ejemplo_grafo_con_error()
    
    print("\n" + "="*70)
    print("✅ EJEMPLOS COMPLETADOS")
    print("="*70)
    print("\n💡 Así es como integras el agente syntax_validator en un grafo LangGraph!")
    print("📚 Los otros agentes (semantic, complexity, optimizer) seguirán el mismo patrón.")
    print()
