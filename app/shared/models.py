"""
Modelos Pydantic compartidos para el sistema de análisis de complejidad algorítmica.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Union

# -----------------------------------------------------------------------------
# Tipos básicos
# -----------------------------------------------------------------------------

Case = Literal["best", "avg", "worst"]


# -----------------------------------------------------------------------------
# Entrada y validación de pseudocódigo
# -----------------------------------------------------------------------------

class PseudocodeIn(BaseModel):
    """Entrada del usuario (pseudocódigo o NL normalizado a pseudo)."""
    text: str = Field(..., description="Texto del pseudocódigo a analizar")
    language_hint: Optional[str] = Field(
        default="es",
        description="Idioma del pseudocódigo (es/en)"
    )


class ErrorItem(BaseModel):
    """Detalle de un error de validación/parseo."""
    linea: Optional[int] = Field(default=None, description="Número de línea del error")
    columna: Optional[int] = Field(default=None, description="Número de columna del error")
    regla: Optional[str] = Field(default=None, description="Regla gramatical violada")
    detalle: Optional[str] = Field(default=None, description="Descripción detallada del error")
    sugerencia: Optional[str] = Field(default=None, description="Sugerencia de corrección")


class SyntaxValidationResult(BaseModel):
    """Resultado de la validación sintáctica."""
    era_algoritmo_valido: bool = Field(..., description="¿El pseudocódigo es válido?")
    codigo_corregido: str = Field(..., description="Código normalizado/corregido")
    errores: List[ErrorItem] = Field(default_factory=list, description="Errores encontrados")
    normalizaciones: List[str] = Field(default_factory=list, description="Normalizaciones aplicadas")
    hints: Dict[str, Union[str, bool, int]] = Field(default_factory=dict, description="Metadatos/hints")


class ASTResult(BaseModel):
    """AST serializado y metadatos de parseo."""
    success: bool = Field(..., description="Indica si el parseo fue exitoso")
    ast: Optional[Dict] = Field(default=None, description="AST como diccionario")
    metadata: Dict = Field(default_factory=dict, description="Metadatos del AST")
    error: Optional[str] = Field(default=None, description="Error si falló el parseo")


# -----------------------------------------------------------------------------
# Modelos para Cost Analyzer
# -----------------------------------------------------------------------------

class CostExpr(BaseModel):
    """Expresión de costo (en notación simbólica tipo Sum) para cada caso."""
    best: str = Field(..., description="Costo mejor caso")
    avg: str = Field(..., description="Costo caso promedio")
    worst: str = Field(..., description="Costo peor caso")


class LoopInfo(BaseModel):
    """Datos de un loop para enriquecer costos por línea."""
    var: str = Field(..., description="Variable del loop (e.g., i, j)")
    start: str = Field(..., description="Inicio del rango (inclusivo)")
    end: str = Field(..., description="Fin del rango (inclusivo)")


class NodeCost(BaseModel):
    """Costo de un nodo del AST (para trazabilidad y per-line)."""
    node_id: str = Field(..., description="Identificador único del nodo")
    node_type: str = Field(..., description="Tipo de nodo (For, If, Assign, ...)")
    line_start: Optional[int] = Field(default=None, description="Línea de inicio (1-indexed)")
    line_end: Optional[int] = Field(default=None, description="Línea de fin (1-indexed)")
    code_snippet: Optional[str] = Field(default=None, description="Fragmento de código")
    cost: CostExpr = Field(..., description="Costo del BLOQUE (incluye hijos)")
    own_cost: Optional[CostExpr] = Field(default=None, description="Costo PROPIO (sin hijos)")
    execution_count: Optional[CostExpr] = Field(
        default=None,
        description="(Reservado) Multiplicadores de ejecución"
    )
    loop_info: Optional[LoopInfo] = Field(default=None, description="Si es For, info de rango")


class LineCost(BaseModel):
    """Costo agregado por línea del código fuente."""
    line_number: int = Field(..., description="Número de línea (1-indexed)")
    code: str = Field(..., description="Texto de la línea")
    operations: List[str] = Field(default_factory=list, description="Nodos/ops en la línea")
    cost: CostExpr = Field(..., description="Costo total de la línea")


class CostsOut(BaseModel):
    """Resultado del análisis de costos."""
    per_node: List[NodeCost] = Field(default_factory=list, description="Costos por nodo (trazabilidad)")
    per_line: List[LineCost] = Field(default_factory=list, description="Costos por línea (para el solver)")
    total: CostExpr = Field(..., description="Costo total simbólico del programa")


# -----------------------------------------------------------------------------
# Modelos para Series Solver
# -----------------------------------------------------------------------------

class SolutionStep(BaseModel):
    """Un paso del proceso de resolución de sumatorias."""
    step_number: int = Field(..., description="Ordinal del paso")
    description: str = Field(..., description="Descripción breve del paso")
    expression: str = Field(..., description="Expresión resultante en el paso")
    case: Case = Field(..., description="Caso (best/avg/worst)")


class ExactCosts(BaseModel):
    """Expresiones exactas (sin sumatorias)."""
    best: str = Field(..., description="Expresión exacta mejor caso")
    avg: str = Field(..., description="Expresión exacta caso promedio")
    worst: str = Field(..., description="Expresión exacta peor caso")


class AsymptoticBounds(BaseModel):
    """Cotas asintóticas finales."""
    omega: str = Field(..., description="Ω(...)")
    theta: str = Field(..., description="Θ(...)")
    big_o: str = Field(..., description="O(...)")


class SolveOut(BaseModel):
    """Salida del solver (por bloques y por líneas)."""
    steps: List[SolutionStep] = Field(default_factory=list, description="Pasos (por bloques)")
    steps_by_line: List[SolutionStep] = Field(default_factory=list, description="Pasos (por línea)")
    exact: ExactCosts = Field(..., description="Costos exactos simplificados")
    big_o: ExactCosts = Field(..., description="Término dominante (Big-O) por caso")
    bounds: AsymptoticBounds = Field(..., description="Ω/Θ/O finales")


# -----------------------------------------------------------------------------
# Respuesta completa para Frontend
# -----------------------------------------------------------------------------

class CompleteAnalysisResult(BaseModel):
    """Respuesta integral del pipeline (para consumo del frontend)."""
    input_text: str = Field(..., description="Texto de entrada original")
    validation: SyntaxValidationResult = Field(..., description="Validación sintáctica")
    ast: ASTResult = Field(..., description="AST y metadatos")
    costs: CostsOut = Field(..., description="Costos simbólicos")
    solution: SolveOut = Field(..., description="Resolución y cotas asintóticas")
    metadata: Dict = Field(default_factory=dict, description="Metadatos del pipeline")


# Exportaciones
__all__ = [
    "Case",
    "PseudocodeIn",
    "ErrorItem",
    "SyntaxValidationResult",
    "ASTResult",
    "CostExpr",
    "LoopInfo",
    "NodeCost",
    "LineCost",
    "CostsOut",
    "SolutionStep",
    "ExactCosts",
    "AsymptoticBounds",
    "SolveOut",
    "CompleteAnalysisResult",
]
