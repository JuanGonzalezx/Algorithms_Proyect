"""
Rutas API para el sistema de análisis de complejidad algorítmica.
"""
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
import logging

from app.shared.models import (
    PseudocodeIn, 
    SyntaxValidationResult, 
    ASTResult, 
    CostsOut, 
    SolveOut,
    CompleteAnalysisResult
)
from app.modules.syntax_validator.agent import get_syntax_validator
from app.modules.parser.service import get_parser_agent
from app.modules.analyzer.cost_model import get_cost_analyzer
from app.modules.solver.solver import get_series_solver
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

# Router principal (sin prefijo, se agrega en main.py)
router = APIRouter(tags=["agents"])


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def _detect_natural_language(text: str) -> bool:
    """
    Detecta si el texto es lenguaje natural o pseudocódigo estructurado.
    
    Heurística simple:
    - Si tiene palabras clave de pseudocódigo (procedimiento, begin, end, for, while, if),
      probablemente ES pseudocódigo
    - Si tiene oraciones en español sin estructura, probablemente ES lenguaje natural
    
    Args:
        text: Texto a analizar
        
    Returns:
        True si es lenguaje natural, False si es pseudocódigo
    """
    text_lower = text.lower()
    
    # Palabras clave del pseudocódigo
    pseudocode_keywords = [
        'procedimiento', 'procedure', 'function', 'funcion',
        'begin', 'end', 'inicio', 'fin',
        'for', 'para', 'while', 'mientras',
        'if', 'si', 'then', 'entonces',
        'return', 'retornar', 'retorna',
        'do', 'hacer'
    ]
    
    # Contar palabras clave de pseudocódigo
    keyword_count = sum(1 for keyword in pseudocode_keywords if keyword in text_lower)
    
    # Si tiene 3 o más palabras clave, probablemente es pseudocódigo
    if keyword_count >= 3:
        return False
    
    # Si tiene símbolos típicos de pseudocódigo
    if '🡨' in text or '<-' in text or ':=' in text:
        return False
    
    # Patrones que sugieren lenguaje natural
    natural_indicators = [
        'quiero', 'necesito', 'crea', 'implementa', 'hacer',
        'algoritmo que', 'programa que', 'función que',
        'ordena', 'busca', 'encuentra', 'calcula'
    ]
    
    natural_count = sum(1 for indicator in natural_indicators if indicator in text_lower)
    
    # Si tiene indicadores de lenguaje natural y pocas palabras clave
    if natural_count > 0 and keyword_count < 2:
        return True
    
    # Por defecto, si es ambiguo y es corto, asumir lenguaje natural
    # Si es largo y estructurado, asumir pseudocódigo
    lines = text.split('\n')
    if len(lines) < 3 and len(text) < 200:
        return True  # Probablemente una descripción corta
    
    return False  # Asumir pseudocódigo por defecto


@router.post(
    "/validate-syntax",
    response_model=SyntaxValidationResult,
    status_code=status.HTTP_200_OK,
    summary="Validar sintaxis de pseudocódigo",
    description="Valida la sintaxis del pseudocódigo usando el agente de validación sintáctica."
)
async def validate_syntax(pseudocode: PseudocodeIn) -> SyntaxValidationResult:
    """
    Endpoint para validar la sintaxis del pseudocódigo.
    
    Args:
        pseudocode: Entrada con el texto del pseudocódigo
        
    Returns:
        SyntaxValidationResult: Resultado de la validación con errores y normalizaciones
        
    Raises:
        HTTPException: Si ocurre un error durante la validación
    """
    try:
        logger.info(f"Validando sintaxis para pseudocódigo de {len(pseudocode.text)} caracteres")
        
        # Obtener el agente de validación sintáctica
        validator = get_syntax_validator()
        
        # Validar
        result = validator.validate(pseudocode)
        
        logger.info(
            f"Validación completada: válido={result.era_algoritmo_valido}, "
            f"errores={len(result.errores)}, normalizaciones={len(result.normalizaciones)}"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error durante validación de sintaxis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno durante la validación: {str(e)}"
        )


@router.post(
    "/parse",
    response_model=ASTResult,
    status_code=status.HTTP_200_OK,
    summary="Parsear pseudocódigo a AST",
    description="Convierte pseudocódigo a AST (Árbol de Sintaxis Abstracta) custom usando el agente parser."
)
async def parse_pseudocode(pseudocode: PseudocodeIn) -> ASTResult:
    """
    Endpoint para convertir pseudocódigo a AST.
    
    Args:
        pseudocode: Entrada con el texto del pseudocódigo
        
    Returns:
        ASTResult: AST serializado con metadatos
        
    Raises:
        HTTPException: Si ocurre un error durante el parsing
    """
    try:
        logger.info(f"Parseando pseudocódigo de {len(pseudocode.text)} caracteres")
        
        # Obtener el agente parser
        parser = get_parser_agent()
        
        # Parsear a AST
        ast_program = parser.parse(pseudocode.text)
        
        # Serializar AST a diccionario
        ast_dict = ast_program.to_dict()
        
        # Calcular metadatos
        num_functions = len(ast_program.functions)
        
        # Contar nodos recursivamente
        def count_nodes(obj) -> int:
            if isinstance(obj, dict):
                return 1 + sum(count_nodes(v) for v in obj.values())
            elif isinstance(obj, list):
                return sum(count_nodes(item) for item in obj)
            else:
                return 0
        
        num_nodes = count_nodes(ast_dict)
        
        result = ASTResult(
            success=True,
            ast=ast_dict,
            metadata={
                "num_functions": num_functions,
                "num_nodes": num_nodes,
                "function_names": [f.name for f in ast_program.functions]
            },
            error=None
        )
        
        logger.info(
            f"Parsing completado: {num_functions} funciones, {num_nodes} nodos"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error durante parsing: {e}", exc_info=True)
        
        # Retornar error en el modelo (no HTTP 500)
        return ASTResult(
            success=False,
            ast=None,
            metadata={},
            error=str(e)
        )


@router.post(
    "/costs",
    response_model=CostsOut,
    status_code=status.HTTP_200_OK,
    summary="Analizar costos algorítmicos",
    description="Convierte el pseudocódigo a sumatorias de costo simbólicas."
)
async def analyze_costs(pseudocode: PseudocodeIn) -> CostsOut:
    """
    Endpoint para analizar costos algorítmicos.
    
    Flujo completo:
    1. Valida sintaxis (syntax_validator)
    2. Parsea a AST (parser)
    3. Analiza costos (cost_analyzer)
    
    Args:
        pseudocode: Entrada con el texto del pseudocódigo
        
    Returns:
        CostsOut: Costos por nodo y total
        
    Raises:
        HTTPException: Si ocurre un error durante el análisis
    """
    try:
        logger.info(f"Analizando costos para pseudocódigo de {len(pseudocode.text)} caracteres")
        
        # Paso 1: Validar sintaxis
        validator = get_syntax_validator()
        validation = validator.validate(pseudocode)
        
        if not validation.era_algoritmo_valido:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "El pseudocódigo tiene errores de sintaxis",
                    "errores": [e.dict() for e in validation.errores]
                }
            )
        
        # Paso 2: Parsear a AST
        parser = get_parser_agent()
        ast_program = parser.parse(validation.codigo_corregido)
        
        # Paso 3: Analizar costos
        analyzer = get_cost_analyzer()
        costs = analyzer.analyze(ast_program)
        
        logger.info(
            f"Análisis completado: {len(costs.per_node)} nodos analizados"
        )
        
        return costs
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error durante análisis de costos: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno durante el análisis: {str(e)}"
        )


@router.post(
    "/solve",
    response_model=SolveOut,
    status_code=status.HTTP_200_OK,
    summary="Pipeline completo: validar → parsear → analizar → resolver",
    description="Ejecuta el pipeline completo desde pseudocódigo hasta cotas asintóticas (Ω, Θ, O)."
)
async def solve_complexity(pseudocode: PseudocodeIn) -> SolveOut:
    """
    Endpoint para ejecutar el pipeline completo de análisis.
    
    Pipeline:
    1. Validar sintaxis
    2. Parsear a AST
    3. Analizar costos (sumatorias)
    4. Resolver sumatorias y calcular Ω, Θ, O
    
    Args:
        pseudocode: Entrada con el texto del pseudocódigo
        
    Returns:
        SolveOut: Costos exactos, Big-O y cotas asintóticas
        
    Raises:
        HTTPException: Si ocurre un error en alguna etapa del pipeline
    """
    try:
        logger.info(f"Iniciando pipeline completo para {len(pseudocode.text)} caracteres")
        
        # PASO 1: Validar sintaxis
        validator = get_syntax_validator()
        validation = validator.validate(pseudocode)
        
        if not validation.era_algoritmo_valido:
            error_details = "; ".join([e.detalle or "Error desconocido" for e in validation.errores])
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Errores de sintaxis: {error_details}"
            )
        
        logger.info("✓ Sintaxis validada")
        
        # PASO 2: Parsear a AST
        parser = get_parser_agent()
        ast = parser.parse(validation.codigo_corregido)
        
        logger.info("✓ AST generado")
        
        # PASO 3: Analizar costos
        analyzer = get_cost_analyzer()
        costs = analyzer.analyze(ast)
        
        logger.info(f"✓ Costos analizados: {len(costs.per_node)} nodos")
        
        # PASO 4: Resolver sumatorias (con ambos métodos: por bloques y por líneas)
        solver = get_series_solver()
        solution = solver.solve(costs.total, show_steps=True, per_line_costs=costs.per_line)
        
        logger.info("✓ Sumatorias resueltas")
        logger.info(f"  Big-O peor caso: {solution.big_o.worst}")
        logger.info(f"  Theta: {solution.bounds.theta}")
        
        return solution
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error en pipeline completo: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno durante el análisis: {str(e)}"
        )


@router.post(
    "/analyze",
    response_model=CompleteAnalysisResult,
    status_code=status.HTTP_200_OK,
    summary="🚀 Análisis completo: Lenguaje Natural → AST → Costos → Big-O",
    description="""
    **Endpoint principal para el frontend**: Un solo botón, un solo endpoint.
    
    Acepta tanto **lenguaje natural** como **pseudocódigo**:
    - Si detecta lenguaje natural, usa Gemini para normalizarlo a pseudocódigo
    - Si ya es pseudocódigo, lo valida y corrige directamente
    
    Luego ejecuta el pipeline completo de 4 agentes y devuelve TODA la información:
    1. 🔍 Validación sintáctica (normalización y corrección)
    2. 🌳 AST (Abstract Syntax Tree con metadatos)
    3. 📊 Análisis de costos (sumatorias sin resolver)
    4. 🎯 Solución (sumatorias resueltas, Big-O, cotas Ω/Θ/O)
    """
)
async def analyze_complete(pseudocode: PseudocodeIn) -> CompleteAnalysisResult:
    """
    Endpoint completo para el frontend: devuelve toda la información de los 4 agentes.
    
    Pipeline:
    1. Validar sintaxis (normalizar si es necesario)
    2. Parsear a AST (con metadatos)
    3. Analizar costos (sumatorias sin resolver)
    4. Resolver sumatorias (expresiones exactas + Big-O + Ω/Θ/O)
    
    Args:
        pseudocode: Entrada con el texto (pseudocódigo o lenguaje natural)
        
    Returns:
        CompleteAnalysisResult: Objeto con toda la información de los 4 agentes
        
    Raises:
        HTTPException: Si ocurre un error en alguna etapa del pipeline
    """
    try:
        logger.info(f"🚀 Iniciando análisis completo para {len(pseudocode.text)} caracteres")
        
        # PASO 0: Detectar si es lenguaje natural o pseudocódigo
        input_text = pseudocode.text.strip()
        is_natural_language = _detect_natural_language(input_text)
        
        if is_natural_language:
            logger.info("🔍 Detectado lenguaje natural - Normalizando con Gemini...")
            try:
                # Normalizar a pseudocódigo usando Gemini
                normalized_pseudocode = await gemini_service.normalize_to_pseudocode(input_text)
                logger.info("✓ Normalización completada")
                logger.info(f"  Pseudocódigo generado: {len(normalized_pseudocode)} caracteres")
                
                # Actualizar el texto a analizar
                pseudocode.text = normalized_pseudocode
            except Exception as gemini_error:
                logger.error(f"❌ Error al normalizar con Gemini: {gemini_error}")
                # Si Gemini falla, NO podemos continuar porque no tenemos pseudocódigo válido
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail={
                        "message": "El servicio de normalización de lenguaje natural no está disponible",
                        "error": str(gemini_error),
                        "suggestion": "Por favor, proporciona el algoritmo en pseudocódigo o intenta nuevamente en unos momentos"
                    }
                )
        else:
            logger.info("✓ Detectado pseudocódigo - Validando directamente...")
        
        # PASO 1: Validar sintaxis
        logger.info("[1/4] Validando sintaxis...")
        validator = get_syntax_validator()
        validation = validator.validate(pseudocode)
        
        if not validation.era_algoritmo_valido:
            # Aún con errores, devolver la información disponible
            logger.warning(f"⚠️ Errores de sintaxis encontrados: {len(validation.errores)}")
            # Intentar continuar con el código corregido si está disponible
            if not validation.codigo_corregido or len(validation.errores) > 5:
                # Demasiados errores, no podemos continuar
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "message": "El código tiene errores de sintaxis que impiden el análisis",
                        "errors": [
                            {
                                "line": e.linea,
                                "column": e.columna,
                                "detail": e.detalle,
                                "suggestion": e.sugerencia
                            }
                            for e in validation.errores
                        ]
                    }
                )
        
        logger.info("✓ [1/4] Sintaxis validada")
        
        # PASO 2: Parsear a AST
        logger.info("[2/4] Parseando AST...")
        parser = get_parser_agent()
        
        try:
            ast_obj = parser.parse(validation.codigo_corregido)
            
            # Crear ASTResult con metadatos
            ast_result = ASTResult(
                success=True,
                ast=ast_obj.to_dict(),
                metadata={
                    "functions": len(ast_obj.functions) if hasattr(ast_obj, 'functions') else 0,
                    "total_nodes": sum(
                        len(func.body.statements) if hasattr(func, 'body') else 0
                        for func in (ast_obj.functions if hasattr(ast_obj, 'functions') else [])
                    )
                }
            )
            
            logger.info(f"✓ [2/4] AST generado ({ast_result.metadata.get('functions', 0)} funciones)")
            
        except Exception as parse_error:
            logger.error(f"❌ Error al parsear: {parse_error}")
            
            # Si el parser falla y aún NO hemos intentado normalizar con Gemini, hacerlo ahora
            if not is_natural_language:
                logger.info("🔄 Código con errores de sintaxis - Intentando normalizar con Gemini...")
                logger.info(f"   Código original: {input_text[:100]}...")
                try:
                    # Normalizar el código con Gemini
                    normalized_pseudocode = await gemini_service.normalize_to_pseudocode(
                        input_text,
                        hint="Este código tiene errores de sintaxis. Por favor corrígelo y devuélvelo en pseudocódigo válido."
                    )
                    logger.info(f"✓ Código normalizado con Gemini ({len(normalized_pseudocode)} caracteres)")
                    logger.info(f"   Código normalizado: {normalized_pseudocode[:100]}...")
                    
                    # Volver a validar
                    pseudocode.text = normalized_pseudocode
                    validation = validator.validate(pseudocode)
                    
                    # Volver a parsear con el código corregido
                    try:
                        ast_obj = parser.parse(validation.codigo_corregido)
                        
                        ast_result = ASTResult(
                            success=True,
                            ast=ast_obj.to_dict(),
                            metadata={
                                "functions": len(ast_obj.functions) if hasattr(ast_obj, 'functions') else 0,
                                "total_nodes": sum(
                                    len(func.body.statements) if hasattr(func, 'body') else 0
                                    for func in (ast_obj.functions if hasattr(ast_obj, 'functions') else [])
                                ),
                                "normalized_by_gemini": True
                            }
                        )
                        
                        logger.info("✓ [2/4] AST generado exitosamente después de normalización")
                        
                    except Exception as second_parse_error:
                        logger.error(f"❌ Fallo al parsear incluso después de normalización: {second_parse_error}")
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"El código no pudo ser parseado incluso después de normalización: {str(second_parse_error)}"
                        )
                        
                except Exception as gemini_error:
                    logger.error(f"❌ Error al normalizar con Gemini: {gemini_error}")
                    logger.error(f"   Tipo de error: {type(gemini_error).__name__}")
                    import traceback
                    logger.error(f"   Traceback: {traceback.format_exc()}")
                    
                    # Extraer información del error
                    gemini_error_msg = str(gemini_error)
                    
                    # Si es una HTTPException, extraer el detalle
                    if isinstance(gemini_error, HTTPException):
                        gemini_error_msg = str(gemini_error.detail) if hasattr(gemini_error, 'detail') else "Error HTTP en Gemini"
                    
                    # Si Gemini también falla, devolver el error original del parser
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "message": "Error al parsear el código",
                            "parse_error": str(parse_error),
                            "normalization_failed": gemini_error_msg if gemini_error_msg else "Error desconocido en Gemini",
                            "gemini_error_type": type(gemini_error).__name__,
                            "suggestion": "Verifica la sintaxis del pseudocódigo o proporciona una descripción en lenguaje natural"
                        }
                    )
            else:
                # Ya intentamos con Gemini y aún falló
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Error al parsear el código normalizado: {str(parse_error)}"
                )
        
        # PASO 3: Analizar costos
        logger.info("[3/4] Analizando costos...")
        analyzer = get_cost_analyzer()
        costs = analyzer.analyze(ast_obj, validation.codigo_corregido)
        
        logger.info(f"✓ [3/4] Costos analizados ({len(costs.per_node)} nodos, {len(costs.per_line)} líneas)")
        
        # PASO 4: Resolver sumatorias (por bloques y por líneas)
        logger.info("[4/4] Resolviendo sumatorias...")
        solver = get_series_solver()
        solution = solver.solve(costs.total, show_steps=True, per_line_costs=costs.per_line)
        
        logger.info("✓ [4/4] Sumatorias resueltas")
        logger.info(f"  📊 Best: {solution.exact.best}")
        logger.info(f"  📊 Avg:  {solution.exact.avg}")
        logger.info(f"  📊 Worst: {solution.exact.worst}")
        logger.info(f"  🎯 Big-O: {solution.bounds.big_o}")
        
        # Construir respuesta completa
        result = CompleteAnalysisResult(
            input_text=input_text,  # El texto original del usuario
            validation=validation,
            ast=ast_result,
            costs=costs,
            solution=solution,
            metadata={
                "pipeline_stages": 5 if is_natural_language else 4,
                "used_gemini_normalization": is_natural_language,
                "input_type": "natural_language" if is_natural_language else "pseudocode",
                "total_nodes_analyzed": len(costs.per_node),
                "has_errors": len(validation.errores) > 0,
                "normalizations_applied": len(validation.normalizaciones),
                "final_pseudocode": pseudocode.text  # El pseudocódigo final usado
            }
        )
        
        logger.info("✅ Análisis completo exitoso")
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"❌ Error en análisis completo: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno durante el análisis: {str(e)}"
        )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Verifica el estado del servicio y los agentes."
)
async def health_check() -> Dict[str, Any]:
    """
    Endpoint de health check.
    
    Returns:
        Dict con el estado del servicio y los agentes
    """
    try:
        # Verificar que los agentes estén disponibles
        validator = get_syntax_validator()
        parser = get_parser_agent()
        analyzer = get_cost_analyzer()
        solver = get_series_solver()
        
        return {
            "status": "healthy",
            "service": "Analizador de Complejidad Algorítmica",
            "agents": {
                "syntax_validator": {
                    "status": "available",
                    "parser": "lark-lalr"
                },
                "parser": {
                    "status": "available",
                    "transformer": "custom-ast"
                },
                "cost_analyzer": {
                    "status": "available",
                    "analyzer": "summation-based"
                },
                "series_solver": {
                    "status": "available",
                    "solver": "sympy-based"
                }
            }
        }
    except Exception as e:
        logger.error(f"Error en health check: {e}", exc_info=True)
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# Exportar router
__all__ = ["router"]
