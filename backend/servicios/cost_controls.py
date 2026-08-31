import os
import datetime
import logging
from typing import List, Dict, Tuple, Any
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger('servicios.cost_controls')

# Constantes de Cost Control
DEFAULT_DAILY_TOKEN_BUDGET = 250_000  # Máximo 250k tokens diarios para toda la plataforma
MAX_HISTORIAL_TURNOS = 10             # Truncar historial a los últimos 10 turnos para optimizar prompt tokens
MAX_TOKENS_CEILING = 1536              # Límite duro para tokens de salida


def _cache_key_presupuesto_diario() -> str:
    hoy = datetime.date.today().isoformat()
    return f"groq_daily_tokens_budget:{hoy}"


def optimizar_historial_turnos(historial: List[Dict[str, str]], max_turnos: int = MAX_HISTORIAL_TURNOS) -> List[Dict[str, str]]:
    """
    Control de Costos: Trunca el historial a los últimos `max_turnos` para evitar
    que la ventana de contexto crezca indefinidamente y consuma tokens excesivos.
    """
    if not historial:
        return []
    
    if len(historial) <= max_turnos:
        return historial

    logger.info(f"Cost Control: Truncando historial de {len(historial)} a los últimos {max_turnos} turnos.")
    return historial[-max_turnos:]


def verificar_presupuesto_diario_tokens() -> Tuple[bool, int, int]:
    """
    Verifica si la plataforma no ha excedido el presupuesto diario global de tokens.

    Returns:
        Tuple (dentro_de_presupuesto: bool, tokens_consumidos: int, presupuesto_maximo: int)
    """
    presupuesto = getattr(settings, 'GROQ_DAILY_GLOBAL_TOKEN_BUDGET', DEFAULT_DAILY_TOKEN_BUDGET)
    cache_key = _cache_key_presupuesto_diario()
    consumo_actual = cache.get(cache_key, 0)

    if consumo_actual >= presupuesto:
        logger.warning(
            f"Cost Control: Presupuesto diario de tokens alcanzado ({consumo_actual}/{presupuesto} tokens)."
        )
        return False, consumo_actual, presupuesto

    return True, consumo_actual, presupuesto


def registrar_consumo_tokens(tokens_utilizados: int) -> int:
    """
    Acumula los tokens utilizados en el contador de caché diario.
    """
    if tokens_utilizados <= 0:
        return 0

    cache_key = _cache_key_presupuesto_diario()
    # Calcular TTL hasta medianoche
    ahora = datetime.datetime.now()
    manana = ahora.date() + datetime.timedelta(days=1)
    medianoche = datetime.datetime.combine(manana, datetime.time.min)
    ttl = max(60, int((medianoche - ahora).total_seconds()))

    try:
        total = cache.incr(cache_key, tokens_utilizados)
    except ValueError:
        cache.set(cache_key, tokens_utilizados, timeout=ttl)
        total = tokens_utilizados

    logger.info(f"Cost Control: +{tokens_utilizados} tokens consumidos. Total diario: {total}")
    return total
