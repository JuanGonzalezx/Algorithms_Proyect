"""
Servicio para construcción de AST desde pseudocódigo.
"""
from typing import Dict
from app.core.psc_parser import PseudocodeParser


def build_ast(content: str, from_lang: str = "pseudocode") -> Dict:
    """
    Construye AST (IR) desde pseudocódigo.
    
    Args:
        content: Pseudocódigo fuente
        from_lang: Debe ser "pseudocode" (parámetro mantenido por compatibilidad)
        
    Returns:
        Dict con el AST serializado
        
    Raises:
        Exception: Si hay errores de parsing
    """
    parser = PseudocodeParser()
    program = parser.build(content)
    return program.to_dict()
