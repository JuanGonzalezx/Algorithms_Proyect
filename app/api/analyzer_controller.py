# app/controllers/analyzer_controller.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

from app.services.ast_service import build_ast  # usa el ParserAgent vía ast_service

logger = logging.getLogger(__name__)

# Router sin prefijo (se agrega en main.py)
router = APIRouter(tags=["analyzer"])


@router.get("/health")
async def health_check():
    """Endpoint de verificación de salud del servicio."""
    return {
        "status": "healthy",
        "service": "Analizador de Complejidades",
        "version": "1.0.0"
    }


# ===== AST (Solo Pseudocódigo) =====

class ASTRequest(BaseModel):
    """Request para construcción de AST desde pseudocódigo."""
    content: str


def _ast_to_dict(node):
    """
    Serializa el AST a dict sin depender de utilidades externas.
    - Si el nodo tiene .to_dict(), lo usa.
    - Si es lista/tupla, serializa recursivo.
    - Si es objeto con __dict__, crea {"type": Clase, ...campos...}.
    - Literales se devuelven tal cual.
    """
    if node is None:
        return None

    # Soporte para nodos con método dedicado
    to_dict = getattr(node, "to_dict", None)
    if callable(to_dict):
        return to_dict()

    # Listas/Tuplas
    if isinstance(node, (list, tuple)):
        return [_ast_to_dict(x) for x in node]

    # Objetos de nuestras clases del AST
    if hasattr(node, "__dict__"):
        data = {"type": node.__class__.__name__}
        for k, v in node.__dict__.items():
            if k.startswith("_"):
                continue
            data[k] = _ast_to_dict(v)
        return data

    # Tipos base (str, int, bool, etc.)
    return node


@router.post("/ast")
async def build_ast_endpoint(req: ASTRequest):
    """
    Construye un AST (IR) desde pseudocódigo y lo devuelve serializado a JSON.
    """
    content = (req.content or "").strip()
    if not content:
        raise HTTPException(status_code=400, detail="'content' es requerido y no puede estar vacío")

    try:
        program = build_ast(content)           # retorna Program (objeto)
        ast_dict = _ast_to_dict(program)       # lo serializamos a dict
        return {"ast": ast_dict}
    except ValueError as e:
        # Errores de parseo / sintaxis
        logger.info(f"Bad pseudocode: {e}")
        raise HTTPException(status_code=400, detail=f"parse_error: {str(e)}")
    except Exception as e:
        logger.error(f"Internal error building AST: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="internal_error: An unexpected error occurred")
