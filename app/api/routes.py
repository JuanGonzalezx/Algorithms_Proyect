# app/controllers/agents_controller.py
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
    CompleteAnalysisResult,
)
from app.modules.syntax_validator.validador import get_syntax_validator
from app.modules.parser.service import get_parser_agent
from app.modules.analyzer.cost_model import get_cost_analyzer          # ← path corregido
from app.modules.solver.solver import get_series_solver     # ← path corregido
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

# Router principal (sin prefijo, se agrega en main.py)
router = APIRouter(tags=["agents"])


# ============================================================================
# AUX
# ============================================================================

def _detect_natural_language(text: str) -> bool:
    """
    Heurística simple para diferenciar lenguaje natural vs. pseudocódigo.
    """
    text_lower = text.lower()

    pseudocode_keywords = [
        "procedimiento", "procedure", "function", "funcion",
        "begin", "end", "inicio", "fin",
        "for", "para", "while", "mientras",
        "if", "si", "then", "entonces",
        "return", "retornar", "retorna",
        "do", "hacer",
    ]
    keyword_count = sum(1 for kw in pseudocode_keywords if kw in text_lower)

    if keyword_count >= 3:
        return False
    if "🡨" in text or "<-" in text or ":=" in text:
        return False

    natural_indicators = [
        "quiero", "necesito", "crea", "implementa", "hacer",
        "algoritmo que", "programa que", "función que",
        "ordena", "busca", "encuentra", "calcula",
    ]
    natural_count = sum(1 for ind in natural_indicators if ind in text_lower)

    if natural_count > 0 and keyword_count < 2:
        return True

    lines = text.split("\n")
    if len(lines) < 3 and len(text) < 200:
        return True

    return False


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post(
    "/validate-syntax",
    response_model=SyntaxValidationResult,
    status_code=status.HTTP_200_OK,
    summary="Validar sintaxis de pseudocódigo",
    description="Valida la sintaxis del pseudocódigo usando el agente de validación sintáctica.",
)
async def validate_syntax(pseudocode: PseudocodeIn) -> SyntaxValidationResult:
    try:
        logger.info(f"Validando sintaxis para pseudocódigo de {len(pseudocode.text)} caracteres")
        validator = get_syntax_validator()
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
            detail=f"Error interno durante la validación: {str(e)}",
        )


@router.post(
    "/parse",
    response_model=ASTResult,
    status_code=status.HTTP_200_OK,
    summary="Parsear pseudocódigo a AST",
    description="Convierte pseudocódigo a AST (IR) usando el parser agent.",
)
async def parse_pseudocode(pseudocode: PseudocodeIn) -> ASTResult:
    try:
        logger.info(f"Parseando pseudocódigo de {len(pseudocode.text)} caracteres")
        parser = get_parser_agent()
        ast_program = parser.parse(pseudocode.text)
        ast_dict = ast_program.to_dict()

        def count_nodes(obj) -> int:
            if isinstance(obj, dict):
                return 1 + sum(count_nodes(v) for v in obj.values())
            if isinstance(obj, list):
                return sum(count_nodes(i) for i in obj)
            return 0

        result = ASTResult(
            success=True,
            ast=ast_dict,
            metadata={
                "num_functions": len(ast_program.functions),
                "num_nodes": count_nodes(ast_dict),
                "function_names": [f.name for f in ast_program.functions],
            },
            error=None,
        )
        logger.info(f"Parsing completado: {result.metadata['num_functions']} funciones, {result.metadata['num_nodes']} nodos")
        return result
    except Exception as e:
        logger.error(f"Error durante parsing: {e}", exc_info=True)
        return ASTResult(success=False, ast=None, metadata={}, error=str(e))


@router.post(
    "/costs",
    response_model=CostsOut,
    status_code=status.HTTP_200_OK,
    summary="Analizar costos algorítmicos",
    description="Convierte el pseudocódigo a sumatorias de costo simbólicas (por línea).",
)
async def analyze_costs(pseudocode: PseudocodeIn) -> CostsOut:
    try:
        logger.info(f"Analizando costos para pseudocódigo de {len(pseudocode.text)} caracteres")

        # 1) Validación
        validator = get_syntax_validator()
        validation = validator.validate(pseudocode)
        if not validation.era_algoritmo_valido:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "El pseudocódigo tiene errores de sintaxis",
                    "errores": [e.dict() for e in validation.errores],
                },
            )

        # 2) Parser
        parser = get_parser_agent()
        ast_program = parser.parse(validation.codigo_corregido)

        # 3) Analyzer (pasamos el código corregido para poder calcular per_line)
        analyzer = get_cost_analyzer()
        costs = analyzer.analyze(ast_program, validation.codigo_corregido)

        logger.info(f"Análisis completado: {len(costs.per_node)} nodos analizados, {len(costs.per_line)} líneas")
        return costs
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error durante análisis de costos: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno durante el análisis: {str(e)}",
        )


@router.post(
    "/solve",
    response_model=SolveOut,
    status_code=status.HTTP_200_OK,
    summary="Pipeline: validar → parsear → analizar → resolver",
    description="Ejecuta el pipeline completo desde pseudocódigo hasta cotas asintóticas (Ω, Θ, O).",
)
async def solve_complexity(pseudocode: PseudocodeIn) -> SolveOut:
    try:
        logger.info(f"Iniciando pipeline para {len(pseudocode.text)} caracteres")

        # 1) Validación
        validator = get_syntax_validator()
        validation = validator.validate(pseudocode)
        if not validation.era_algoritmo_valido:
            error_details = "; ".join([e.detalle or "Error" for e in validation.errores])
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Errores de sintaxis: {error_details}")

        # 2) Parser
        parser = get_parser_agent()
        ast = parser.parse(validation.codigo_corregido)

        # 3) Analyzer (con código para per_line)
        analyzer = get_cost_analyzer()
        costs = analyzer.analyze(ast, validation.codigo_corregido)

        # 4) Solver (sumatorias + Ω/Θ/O). Pasos solo por línea.
        solver = get_series_solver()
        solution = solver.solve(costs.total, show_steps=True, per_line_costs=costs.per_line)

        logger.info("Pipeline completado")
        return solution
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en pipeline: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno durante el análisis: {str(e)}",
        )


@router.post(
    "/analyze",
    response_model=CompleteAnalysisResult,
    status_code=status.HTTP_200_OK,
    summary="Análisis completo: Lenguaje Natural → AST → Costos → Big-O",
    description=(
        "Endpoint principal para el frontend. Acepta lenguaje natural o pseudocódigo, "
        "normaliza con Gemini si es necesario y ejecuta todo el pipeline."
    ),
)
async def analyze_complete(pseudocode: PseudocodeIn) -> CompleteAnalysisResult:
    try:
        logger.info(f"Iniciando análisis completo para {len(pseudocode.text)} caracteres")

        input_text = pseudocode.text.strip()
        is_natural = _detect_natural_language(input_text)

        # Posible normalización vía Gemini
        if is_natural:
            logger.info("Detectado lenguaje natural - Normalizando con Gemini…")
            try:
                normalized_pseudocode = await gemini_service.normalize_to_pseudocode(input_text)
                pseudocode.text = normalized_pseudocode
                logger.info("Normalización completada")
            except Exception as gemini_error:
                logger.error(f"Error al normalizar con Gemini: {gemini_error}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail={
                        "message": "El servicio de normalización no está disponible",
                        "error": str(gemini_error),
                        "suggestion": "Proporcione pseudocódigo válido o intente nuevamente",
                    },
                )

        # 1) Validación
        logger.info("[1/4] Validando sintaxis…")
        validator = get_syntax_validator()
        validation = validator.validate(pseudocode)
        if not validation.era_algoritmo_valido:
            # Si hay demasiados errores, detenemos
            if not validation.codigo_corregido or len(validation.errores) > 5:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "message": "El código tiene errores de sintaxis que impiden el análisis",
                        "errors": [
                            {
                                "line": e.linea,
                                "column": e.columna,
                                "detail": e.detalle,
                                "suggestion": e.sugerencia,
                            }
                            for e in validation.errores
                        ],
                    },
                )
        logger.info("✓ [1/4] Sintaxis validada")

        # 2) Parser
        logger.info("[2/4] Parseando AST…")
        parser = get_parser_agent()
        try:
            ast_obj = parser.parse(validation.codigo_corregido)
            ast_result = ASTResult(
                success=True,
                ast=ast_obj.to_dict(),
                metadata={
                    "functions": len(ast_obj.functions) if hasattr(ast_obj, "functions") else 0,
                    "total_nodes": sum(
                        len(func.body.statements) if hasattr(func, "body") else 0
                        for func in (ast_obj.functions if hasattr(ast_obj, "functions") else [])
                    ),
                },
            )
            logger.info(f"✓ [2/4] AST generado ({ast_result.metadata.get('functions', 0)} funciones)")
        except Exception as parse_error:
            logger.error(f"Error al parsear: {parse_error}")
            # Si venía como pseudocódigo y falló, intentamos una normalización tardía
            if not is_natural:
                try:
                    normalized = await gemini_service.normalize_to_pseudocode(
                        input_text,
                        hint="Corrige la sintaxis y devuelve pseudocódigo válido.",
                    )
                    pseudocode.text = normalized
                    validation = validator.validate(pseudocode)
                    ast_obj = parser.parse(validation.codigo_corregido)
                    ast_result = ASTResult(
                        success=True,
                        ast=ast_obj.to_dict(),
                        metadata={
                            "functions": len(ast_obj.functions) if hasattr(ast_obj, "functions") else 0,
                            "total_nodes": sum(
                                len(func.body.statements) if hasattr(func, "body") else 0
                                for func in (ast_obj.functions if hasattr(ast_obj, "functions") else [])
                            ),
                            "normalized_by_gemini": True,
                        },
                    )
                    logger.info("✓ [2/4] AST generado tras normalización")
                except Exception as second_error:
                    logger.error(f"Fallo tras normalización: {second_error}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"No se pudo parsear el código: {str(second_error)}",
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Error al parsear el código normalizado: {str(parse_error)}",
                )

        # 3) Analyzer (con código para per_line)
        logger.info("[3/4] Analizando costos…")
        analyzer = get_cost_analyzer()
        costs = analyzer.analyze(ast_obj, validation.codigo_corregido)
        logger.info(f"✓ [3/4] Costos analizados ({len(costs.per_node)} nodos, {len(costs.per_line)} líneas)")

        # 4) Solver (sumatorias + Ω/Θ/O). Pasos por línea.
        logger.info("[4/4] Resolviendo sumatorias…")
        solver = get_series_solver()
        solution = solver.solve(costs.total, show_steps=True, per_line_costs=costs.per_line)
        logger.info("✓ [4/4] Sumatorias resueltas")

        result = CompleteAnalysisResult(
            input_text=input_text,
            validation=validation,
            ast=ast_result,
            costs=costs,
            solution=solution,
            metadata={
                "pipeline_stages": 5 if is_natural else 4,
                "used_gemini_normalization": is_natural,
                "input_type": "natural_language" if is_natural else "pseudocode",
                "total_nodes_analyzed": len(costs.per_node),
                "has_errors": len(validation.errores) > 0,
                "normalizations_applied": len(validation.normalizaciones),
                "final_pseudocode": pseudocode.text,
            },
        )
        logger.info("Análisis completo exitoso")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en análisis completo: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno durante el análisis: {str(e)}",
        )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Verifica el estado del servicio.",
)
async def health_check() -> Dict[str, Any]:
    try:
        get_syntax_validator()
        get_parser_agent()
        get_cost_analyzer()
        get_series_solver()
        return {
            "status": "healthy",
            "service": "Analizador de Complejidad Algorítmica",
            "agents": {
                "syntax_validator": {"status": "available", "parser": "lark-lalr"},
                "parser": {"status": "available", "transformer": "custom-ast"},
                "cost_analyzer": {"status": "available", "analyzer": "summation-based"},
                "series_solver": {"status": "available", "solver": "sympy-based"},
            },
        }
    except Exception as e:
        logger.error(f"Error en health check: {e}", exc_info=True)
        return {"status": "unhealthy", "error": str(e)}


__all__ = ["router"]
