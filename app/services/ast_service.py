"""
Servicio para construcción de AST desde pseudocódigo.
"""
from typing import Dict
from app.services.psc_parser import PseudocodeParser


def build_ast(content: str, from_lang: str = "pseudocode") -> Dict:
    """
    Construye AST (IR) desde pseudocódigo.
    
    """
    parser = PseudocodeParser()
    program = parser.build(content)
    return program.to_dict()
