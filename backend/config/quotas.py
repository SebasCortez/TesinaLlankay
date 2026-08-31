import datetime
from django.core.cache import cache
from django.conf import settings
from typing import Tuple, Dict, Any


def _segundos_hasta_medianoche() -> int:
    """
    Calcula los segundos restantes hasta la próxima medianoche local.
    """
    ahora = datetime.datetime.now()
    manana = ahora.date() + datetime.timedelta(days=1)
    medianoche = datetime.datetime.combine(manana, datetime.time.min)
    return max(60, int((medianoche - ahora).total_seconds()))


def _obtener_identificador_cuota(request) -> str:
    """
    Genera el identificador único para el seguimiento de cuota.
    """
    if hasattr(request, 'user') and request.user and request.user.is_authenticated:
        return f"quota_user_{request.user.pk}"
    
    # Extraer IP de cliente
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        ip = x_forwarded.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '127.0.0.1')

    return f"quota_ip_{ip}"


def verificar_y_consumir_cuota(
    request,
    tipo: str = "agente_chat",
    incrementar: bool = True
) -> Tuple[bool, Dict[str, Any]]:
    """
    Verifica si el usuario o IP ha excedido su cuota diaria de uso.

    Args:
        request: Request HTTP de Django.
        tipo: Identificador del tipo de cuota (por defecto 'agente_chat').
        incrementar: Si es True, incrementa el contador al momento de verificar.

    Returns:
        Tuple (permitido: bool, metadata_cuota: dict)
    """
    ident = _obtener_identificador_cuota(request)
    es_autenticado = hasattr(request, 'user') and request.user and request.user.is_authenticated

    # Determinar límite diario según el tipo de usuario
    if es_autenticado:
        limite_diario = getattr(settings, 'GROQ_DAILY_USER_QUOTA', 100)
    else:
        limite_diario = getattr(settings, 'GROQ_DAILY_IP_QUOTA', 40)

    hoy_str = datetime.date.today().isoformat()
    cache_key = f"daily_quota:{tipo}:{hoy_str}:{ident}"
    ttl = _segundos_hasta_medianoche()

    # Obtener uso actual
    uso_actual = cache.get(cache_key, 0)

    if uso_actual >= limite_diario:
        return False, {
            "permitido": False,
            "uso_actual": uso_actual,
            "limite_diario": limite_diario,
            "restantes": 0,
            "segundos_reinicio": ttl,
            "mensaje": f"Has alcanzado tu cuota diaria de {limite_diario} consultas. Tu cuota se reiniciará a la medianoche."
        }

    if incrementar:
        try:
            nuevo_uso = cache.incr(cache_key)
        except ValueError:
            cache.set(cache_key, 1, timeout=ttl)
            nuevo_uso = 1
    else:
        nuevo_uso = uso_actual

    restantes = max(0, limite_diario - nuevo_uso)

    return True, {
        "permitido": True,
        "uso_actual": nuevo_uso,
        "limite_diario": limite_diario,
        "restantes": restantes,
        "segundos_reinicio": ttl,
        "mensaje": None
    }
