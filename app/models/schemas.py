from pydantic import BaseModel, Field
from typing import Optional, List, Any
from enum import Enum

class InputType(str, Enum):
    PSEUDOCODE = "pseudocode"
    NATURAL_LANGUAGE = "natural_language"

class InputRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000, description="Pseudocódigo o descripción en lenguaje natural")
    input_type: Optional[InputType] = Field(None, description="Tipo de entrada. Si no se especifica, se detectará automáticamente")

class PseudocodeResponse(BaseModel):
    original_content: str = Field(..., description="Contenido original enviado")
    normalized_pseudocode: str = Field(..., description="Pseudocódigo normalizado")
    input_type_detected: InputType = Field(..., description="Tipo de entrada detectado")
    is_valid_pseudocode: bool = Field(..., description="Si el pseudocódigo es válido sintácticamente")
    correction_applied: bool = Field(False, description="Si se aplicó corrección con LLM")

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Descripción del error")
    details: Optional[str] = Field(None, description="Detalles adicionales del error")

class ASTNode(BaseModel):
    node_type: str = Field(..., description="Tipo de nodo AST")
    value: Optional[str] = Field(None, description="Valor del nodo si aplica")
    children: List['ASTNode'] = Field(default_factory=list, description="Nodos hijos")
    line: Optional[int] = Field(None, description="Línea en el código fuente")
    column: Optional[int] = Field(None, description="Columna en el código fuente")

class ASTResponse(BaseModel):
    pseudocode: str = Field(..., description="Pseudocódigo analizado")
    ast: ASTNode = Field(..., description="Árbol sintáctico abstracto")
    parse_successful: bool = Field(..., description="Si el parseo fue exitoso")
    error_message: Optional[str] = Field(None, description="Mensaje de error si el parseo falló")

# Necesario para las referencias circulares en ASTNode
ASTNode.model_rebuild()