"""
Modelos Pydantic compartidos para el sistema de análisis de complejidad algorítmica.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Union

# Tipo literal para casos de complejidad
Case = Literal["best", "avg", "worst"]


class PseudocodeIn(BaseModel):
    """Modelo de entrada para pseudocódigo."""
    text: str = Field(..., description="Texto del pseudocódigo a analizar")
    language_hint: Optional[str] = Field(
        default="es",
        description="Idioma del pseudocódigo (es/en)"
    )


class ErrorItem(BaseModel):
    """Detalle de un error de sintaxis o validación."""
    linea: Optional[int] = Field(default=None, description="Número de línea del error")
    columna: Optional[int] = Field(default=None, description="Número de columna del error")
    regla: Optional[str] = Field(default=None, description="Regla gramatical violada")
    detalle: Optional[str] = Field(default=None, description="Descripción detallada del error")
    sugerencia: Optional[str] = Field(default=None, description="Sugerencia de corrección")


class SyntaxValidationResult(BaseModel):
    """Resultado de la validación sintáctica del pseudocódigo."""
    era_algoritmo_valido: bool = Field(
        ...,
        description="Indica si el pseudocódigo era sintácticamente válido"
    )
    codigo_corregido: str = Field(
        ...,
        description="Código normalizado o corregido"
    )
    errores: List[ErrorItem] = Field(
        default_factory=list,
        description="Lista de errores encontrados"
    )
    normalizaciones: List[str] = Field(
        default_factory=list,
        description="Lista de normalizaciones aplicadas"
    )
    hints: Dict[str, Union[str, bool, int]] = Field(
        default_factory=dict,
        description="Sugerencias y metadatos adicionales"
    )


class ASTNode(BaseModel):
    """Representación serializable de un nodo del AST."""
    type: str = Field(..., description="Tipo del nodo AST")
    data: Dict = Field(..., description="Datos del nodo en formato diccionario")
    
    class Config:
        # Permitir tipos arbitrarios para poder manejar objetos de ast_nodes.py
        arbitrary_types_allowed = True


class ASTResult(BaseModel):
    """Resultado del parsing: AST + metadatos."""
    success: bool = Field(..., description="Indica si el parsing fue exitoso")
    ast: Optional[Dict] = Field(
        default=None,
        description="AST serializado como diccionario (null si hay error)"
    )
    metadata: Dict = Field(
        default_factory=dict,
        description="Metadatos del AST: número de funciones, nodos, etc."
    )
    error: Optional[str] = Field(
        default=None,
        description="Mensaje de error si el parsing falló"
    )


# ============================================================================
# MODELOS PARA COST ANALYZER
# ============================================================================

class CostExpr(BaseModel):
    """Expresión de costo en los tres casos: mejor, promedio, peor."""
    best: str = Field(..., description="Costo en el mejor caso (notación Sum)")
    avg: str = Field(..., description="Costo en el caso promedio (notación Sum)")
    worst: str = Field(..., description="Costo en el peor caso (notación Sum)")


class LoopInfo(BaseModel):
    """Información de un loop (para costos por línea)."""
    var: str = Field(..., description="Variable del loop (e.g., 'i', 'j')")
    start: str = Field(..., description="Valor inicial del loop (e.g., '1')")
    end: str = Field(..., description="Valor final del loop (e.g., 'n-1')")


class NodeCost(BaseModel):
    """Costo de un nodo individual del AST."""
    node_id: str = Field(..., description="Identificador único del nodo")
    node_type: str = Field(..., description="Tipo del nodo AST (For, If, Assign, etc.)")
    line_start: Optional[int] = Field(
        default=None, 
        description="Línea de inicio del nodo en el código fuente (1-indexed)"
    )
    line_end: Optional[int] = Field(
        default=None,
        description="Línea de fin del nodo en el código fuente (1-indexed)"
    )
    code_snippet: Optional[str] = Field(
        default=None,
        description="Fragmento de código correspondiente al nodo"
    )
    cost: CostExpr = Field(..., description="Costo del nodo en los tres casos (costo de BLOQUE, incluye hijos)")
    own_cost: Optional[CostExpr] = Field(
        default=None,
        description="Costo propio del nodo sin incluir hijos (para costos por línea)"
    )
    execution_count: Optional[CostExpr] = Field(
        default=None,
        description="Número de veces que se ejecuta esta línea (multiplicador de loops padre)"
    )
    loop_info: Optional[LoopInfo] = Field(
        default=None,
        description="Información del loop si este nodo es un For (variable, inicio, fin)"
    )


class LineCost(BaseModel):
    """Costo de una línea individual del código fuente."""
    line_number: int = Field(..., description="Número de línea (1-indexed)")
    code: str = Field(..., description="Código fuente de la línea")
    operations: List[str] = Field(
        default_factory=list,
        description="Lista de operaciones/nodos en esta línea"
    )
    cost: CostExpr = Field(..., description="Costo total de la línea (suma de operaciones)")


class CostsOut(BaseModel):
    """Resultado del análisis de costos: costos por nodo y total."""
    per_node: List[NodeCost] = Field(
        default_factory=list,
        description="Lista de costos por cada nodo del AST (costos de BLOQUE)"
    )
    per_line: List[LineCost] = Field(
        default_factory=list,
        description="Lista de costos por cada línea del código (costos PROPIOS)"
    )
    total: CostExpr = Field(
        ...,
        description="Costo total del programa en los tres casos"
    )


# ============================================================================
# MODELOS PARA SERIES SOLVER
# ============================================================================

class SolutionStep(BaseModel):
    """Un paso en el proceso de resolución de sumatorias."""
    step_number: int = Field(..., description="Número de paso en la secuencia")
    description: str = Field(..., description="Descripción del paso (ej: 'Expresión inicial', 'Resolver sumatoria 1')")
    expression: str = Field(..., description="Expresión matemática en este paso")
    case: Case = Field(..., description="Caso al que aplica este paso")


class ExactCosts(BaseModel):
    """Costos exactos simplificados (sin sumatorias)."""
    best: str = Field(..., description="Expresión exacta simplificada para el mejor caso")
    avg: str = Field(..., description="Expresión exacta simplificada para el caso promedio")
    worst: str = Field(..., description="Expresión exacta simplificada para el peor caso")


class AsymptoticBounds(BaseModel):
    """Cotas asintóticas: Ω (omega), Θ (theta), O (big-o)."""
    omega: str = Field(..., description="Cota inferior asintótica Ω(...)")
    theta: str = Field(..., description="Cota ajustada asintótica Θ(...)")
    big_o: str = Field(..., description="Cota superior asintótica O(...)")


class SolveOut(BaseModel):
    """Resultado del solver: costos exactos y análisis asintótico."""
    steps: List[SolutionStep] = Field(
        default_factory=list,
        description="Proceso paso a paso de resolución (análisis por bloques)"
    )
    steps_by_line: List[SolutionStep] = Field(
        default_factory=list,
        description="Proceso paso a paso sumando cada línea individual"
    )
    exact: ExactCosts = Field(
        ...,
        description="Expresiones exactas simplificadas (sumatorias resueltas)"
    )
    big_o: ExactCosts = Field(
        ...,
        description="Notación Big-O para cada caso (solo términos dominantes)"
    )
    bounds: AsymptoticBounds = Field(
        ...,
        description="Cotas asintóticas completas (Ω, Θ, O)"
    )


# ============================================================================
# MODELO PARA RESPUESTA COMPLETA (FRONTEND)
# ============================================================================

class CompleteAnalysisResult(BaseModel):
    """
    Resultado completo del análisis: incluye toda la información de los 4 agentes.
    Diseñado para consumo directo desde el frontend.
    """
    # Input original
    input_text: str = Field(..., description="Texto de entrada (pseudocódigo o lenguaje natural)")
    
    # Agente 1: Syntax Validator
    validation: SyntaxValidationResult = Field(
        ...,
        description="Resultado de la validación sintáctica"
    )
    
    # Agente 2: Parser
    ast: ASTResult = Field(
        ...,
        description="AST generado y sus metadatos"
    )
    
    # Agente 3: Cost Analyzer
    costs: CostsOut = Field(
        ...,
        description="Análisis de costos (sumatorias sin resolver)"
    )
    
    # Agente 4: Series Solver
    solution: SolveOut = Field(
        ...,
        description="Sumatorias resueltas y cotas asintóticas"
    )
    
    # Metadatos del análisis
    metadata: Dict = Field(
        default_factory=dict,
        description="Metadatos adicionales del análisis completo"
    )


# Exportar todos los modelos
__all__ = [
    "Case",
    "PseudocodeIn",
    "ErrorItem",
    "SyntaxValidationResult",
    "ASTNode",
    "ASTResult",
    "CostExpr",
    "NodeCost",
    "CostsOut",
    "ExactCosts",
    "AsymptoticBounds",
    "SolveOut",
    "CompleteAnalysisResult",
]
