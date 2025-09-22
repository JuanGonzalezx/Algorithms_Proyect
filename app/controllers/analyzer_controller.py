from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    InputRequest, PseudocodeResponse, ASTResponse, ErrorResponse, 
    InputType, ASTNode as SchemaASTNode
)
from app.core.classifier import input_classifier
from app.core.parser import pseudocode_parser
from app.services.gemini_service import gemini_service
from app.models.ast_nodes import ASTNode
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["analyzer"])

@router.post("/classify", response_model=dict)
async def classify_input(request: InputRequest):
    """
    Clasifica si el input es pseudocódigo o lenguaje natural
    """
    try:
        input_type, confidence = input_classifier.classify_input(request.content)
        
        return {
            "content": request.content,
            "detected_type": input_type,
            "confidence": confidence,
            "classification_successful": True
        }
        
    except Exception as e:
        logger.error(f"Error en clasificación: {e}")
        raise HTTPException(status_code=500, detail=f"Error en clasificación: {str(e)}")

@router.post("/normalize", response_model=PseudocodeResponse)
async def normalize_pseudocode(request: InputRequest):
    """
    Normaliza entrada a pseudocódigo válido.
    Si es lenguaje natural, lo convierte. Si es pseudocódigo con errores, lo corrige.
    """
    try:
        # Clasificar tipo de entrada
        detected_type = request.input_type
        if not detected_type:
            detected_type, _ = input_classifier.classify_input(request.content)
        
        normalized_pseudocode = request.content
        correction_applied = False
        
        # Si es lenguaje natural, convertir a pseudocódigo
        if detected_type == InputType.NATURAL_LANGUAGE:
            normalized_pseudocode = await gemini_service.normalize_to_pseudocode(request.content)
            correction_applied = True
        
        # Validar sintaxis del pseudocódigo
        is_valid, error_message = pseudocode_parser.validate_syntax(normalized_pseudocode)
        
        # Si hay errores sintácticos, intentar corrección con LLM
        if not is_valid and error_message:
            logger.warning(f"Pseudocódigo con errores: {error_message}")
            corrected_pseudocode = await gemini_service.correct_pseudocode(
                normalized_pseudocode, error_message
            )
            
            # Validar la corrección
            is_corrected_valid, _ = pseudocode_parser.validate_syntax(corrected_pseudocode)
            
            if is_corrected_valid:
                normalized_pseudocode = corrected_pseudocode
                is_valid = True
                correction_applied = True
        
        return PseudocodeResponse(
            original_content=request.content,
            normalized_pseudocode=normalized_pseudocode,
            input_type_detected=detected_type,
            is_valid_pseudocode=is_valid,
            correction_applied=correction_applied
        )
        
    except Exception as e:
        logger.error(f"Error en normalización: {e}")
        raise HTTPException(status_code=500, detail=f"Error en normalización: {str(e)}")

@router.post("/parse", response_model=ASTResponse)
async def parse_to_ast(request: InputRequest):
    """
    Parsea pseudocódigo y genera AST.
    Incluye normalización automática si es necesario.
    """
    try:
        # Primero normalizar el pseudocódigo
        normalize_response = await normalize_pseudocode(request)
        
        if not normalize_response.is_valid_pseudocode:
            return ASTResponse(
                pseudocode=normalize_response.normalized_pseudocode,
                ast=SchemaASTNode(node_type="error", value="Invalid pseudocode"),
                parse_successful=False,
                error_message="No se pudo obtener pseudocódigo válido después de la normalización"
            )
        
        # Parsear a AST
        success, ast_root, error_message = pseudocode_parser.parse(
            normalize_response.normalized_pseudocode
        )
        
        if success and ast_root:
            # Convertir AST interno a esquema para respuesta
            schema_ast = _convert_ast_to_schema(ast_root)
            
            return ASTResponse(
                pseudocode=normalize_response.normalized_pseudocode,
                ast=schema_ast,
                parse_successful=True,
                error_message=None
            )
        else:
            return ASTResponse(
                pseudocode=normalize_response.normalized_pseudocode,
                ast=SchemaASTNode(node_type="error", value="Parse failed"),
                parse_successful=False,
                error_message=error_message or "Error desconocido en el parsing"
            )
            
    except Exception as e:
        logger.error(f"Error en parsing: {e}")
        raise HTTPException(status_code=500, detail=f"Error en parsing: {str(e)}")

@router.get("/health")
async def health_check():
    """Endpoint de verificación de salud del servicio"""
    return {
        "status": "healthy",
        "service": "Analizador de Complejidades",
        "version": "1.0.0"
    }

def _convert_ast_to_schema(ast_node: ASTNode) -> SchemaASTNode:
    """
    Convierte nodo AST interno a esquema Pydantic para respuesta
    """
    schema_children = []
    
    if hasattr(ast_node, 'children') and ast_node.children:
        schema_children = [_convert_ast_to_schema(child) for child in ast_node.children]
    
    return SchemaASTNode(
        node_type=ast_node.node_type,
        value=getattr(ast_node, 'value', None),
        children=schema_children,
        line=getattr(ast_node, 'line', None),
        column=getattr(ast_node, 'column', None)
    )