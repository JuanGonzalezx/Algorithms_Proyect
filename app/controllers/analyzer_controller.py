from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
from pathlib import Path
import datetime
from typing import Optional, Literal

from app.services.gemini_service import gemini_service
from app.models.schemas import InputRequest, PseudocodeResponse, InputType
from app.services.ast_service import build_ast

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["analyzer"])



@router.get("/health")
async def health_check():
    """Endpoint de verificación de salud del servicio"""
    return {
        "status": "healthy",
        "service": "Analizador de Complejidades",
        "version": "1.0.0"
    }


class GenerateRequest(BaseModel):
    description: str
    filename: Optional[str] = None


@router.post("/generate")
async def generate_and_save(req: GenerateRequest):
    """Recibe una descripción en lenguaje natural, pide a Gemini el código Python y lo guarda.

    Retorna la ruta del archivo guardado y el código generado.
    """
    if not req.description or not req.description.strip():
        raise HTTPException(status_code=400, detail="'description' es requerido y no puede estar vacío")

    try:
        code = await gemini_service.generate_python_code(req.description)
    except Exception as e:
        logger.error(f"Error llamando a Gemini: {e}")
        raise HTTPException(status_code=500, detail=f"Error generando código: {str(e)}")

    # Guardar el prompt y el código en un archivo dentro de docs/ejemplos/algoritmos_guardados/
    save_dir = Path("docs/ejemplos/algoritmos_guardados").resolve()
    save_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    base_name = req.filename.strip() if req.filename else f"alg_{timestamp}"
    # Asegurar extensión .py
    if not base_name.endswith('.py'):
        base_name = f"{base_name}.py"

    file_path = save_dir / base_name

    # Preparamos el contenido con el prompt como comentario al inicio
    prompt_comment = "# Prompt:\n" + "# " + req.description.replace("\n", "\n# ") + "\n\n"
    try:
        file_path.write_text(prompt_comment + code, encoding="utf-8")
    except Exception as e:
        logger.error(f"Error guardando archivo {file_path}: {e}")
        raise HTTPException(status_code=500, detail=f"Error guardando archivo: {str(e)}")

    return {"saved_path": str(file_path), "code": code}


@router.post("/normalize", response_model=PseudocodeResponse)
async def normalize_to_pseudocode(req: InputRequest):
    """
    Convierte una descripción en lenguaje natural a pseudocódigo normalizado.
    
    Este endpoint recibe una descripción en lenguaje natural y utiliza Gemini
    para generar pseudocódigo estructurado siguiendo la gramática del proyecto.
    """
    if not req.content or not req.content.strip():
        raise HTTPException(status_code=400, detail="'content' es requerido y no puede estar vacío")

    try:
        # Normalizar a pseudocódigo usando Gemini
        normalized = await gemini_service.normalize_to_pseudocode(req.content)
        
        return PseudocodeResponse(
            original_content=req.content,
            normalized_pseudocode=normalized,
            input_type_detected=InputType.NATURAL_LANGUAGE,
            is_valid_pseudocode=True,
            correction_applied=True
        )
    except Exception as e:
        logger.error(f"Error normalizando con Gemini: {e}")
        raise HTTPException(status_code=500, detail=f"Error normalizando: {str(e)}")


@router.post("/generate-code")
async def generate_code(req: InputRequest):
    """
    Genera código Python a partir de una descripción en lenguaje natural o pseudocódigo.
    
    Este endpoint recibe una descripción y retorna código Python implementable.
    Útil para obtener solo el código sin guardarlo.
    """
    if not req.content or not req.content.strip():
        raise HTTPException(status_code=400, detail="'content' es requerido y no puede estar vacío")

    try:
        code = await gemini_service.generate_python_code(req.content)
        
        return {
            "description": req.content,
            "generated_code": code,
            "language": "python"
        }
    except Exception as e:
        logger.error(f"Error generando código con Gemini: {e}")
        raise HTTPException(status_code=500, detail=f"Error generando código: {str(e)}")


# ============================================================================
# ENDPOINT: AST (Solo Pseudocódigo)
# ============================================================================

class ASTRequest(BaseModel):
    """Request para construcción de AST desde pseudocódigo"""
    content: str


@router.post("/ast")
async def build_ast_endpoint(req: ASTRequest):
    """
    Construye un AST (Representación Intermedia) desde pseudocódigo.
    
    Este endpoint parsea pseudocódigo y genera nuestro IR para análisis de complejidad.
    
    Args:
        content: Pseudocódigo fuente
        
    Returns:
        JSON con el AST en formato IR
        
    Errors:
        400: Sintaxis inválida o no soportada
        500: Error interno
    """
    if not req.content or not req.content.strip():
        raise HTTPException(status_code=400, detail="'content' es requerido y no puede estar vacío")
    
    try:
        # Solo pseudocódigo permitido
        ast_dict = build_ast(req.content, from_lang="pseudocode")
        return {"ast": ast_dict}
    
    except NotImplementedError as e:
        # Sintaxis no soportada
        logger.info(f"Unsupported syntax: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"unsupported_syntax: {str(e)}"
        )
    
    except Exception as e:
        # Error inesperado (incluyendo parsing errors)
        logger.error(f"Internal error building AST: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"internal_error: An unexpected error occurred"
        )