"""
Servicio para construcción de AST desde diferentes lenguajes.
Soporta Python y pseudocódigo.
"""
from typing import Dict, Literal
from app.core.py_ast_builder import PythonToIR
from app.core.psc_parser import PseudocodeParser


def build_ast(content: str, from_lang: Literal["python", "pseudocode"] = "python") -> Dict:
    """
    Construye AST (IR) desde código fuente.
    
    Args:
        content: Código fuente
        from_lang: Lenguaje fuente ("python" o "pseudocode")
        
    Returns:
        Dict con el AST serializado
        
    Raises:
        ValueError: Si from_lang no es válido
        SyntaxError: Si el código tiene errores de sintaxis
        NotImplementedError: Si usa características no soportadas (Python)
        Exception: Si hay errores de parsing (pseudocode)
    """
    if from_lang == "python":
        builder = PythonToIR()
        program = builder.build(content)
        return program.to_dict()
    
    elif from_lang == "pseudocode":
        parser = PseudocodeParser()
        program = parser.build(content)
        return program.to_dict()
    
    else:
        raise ValueError(
            f"Language '{from_lang}' not supported. "
            f"Only 'python' and 'pseudocode' are supported."
        )
