import json
import logging
import time
from datetime import datetime, timezone

logger = logging.getLogger('api.metrics')


class APIMetricsMiddleware:
    """
    Middleware de Django para registrar métricas de rendimiento y confiabilidad
    en cada solicitud a la API (volumen, tiempo de respuesta y códigos de estado HTTP).
    
    Emite líneas JSON estructuradas a stdout para que plataformas como Railway
    las capturen automáticamente en los logs de despliegue.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Medir tiempo de inicio de la solicitud con alta resolución
        start_time = time.perf_counter()

        # Procesar la vista / endpoint
        response = self.get_response(request)

        # Medir tiempo final y calcular duración en milisegundos
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Clasificar código de estado
        status_code = response.status_code
        if 200 <= status_code < 300:
            status_class = "2xx"
        elif 300 <= status_code < 400:
            status_class = "3xx"
        elif 400 <= status_code < 500:
            status_class = "4xx"
        elif status_code >= 500:
            status_class = "5xx"
        else:
            status_class = "other"

        # Obtener IP del cliente (considerando proxies/balanceadores como Railway)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            client_ip = x_forwarded_for.split(',')[0].strip()
        else:
            client_ip = request.META.get('REMOTE_ADDR', '')

        # Obtener ID de usuario si está autenticado
        user_id = None
        if hasattr(request, 'user') and request.user and request.user.is_authenticated:
            user_id = request.user.id

        # Estructura de métrica en JSON
        metric_data = {
            "type": "api_metric",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "method": request.method,
            "path": request.path,
            "status_code": status_code,
            "status_class": status_class,
            "duration_ms": duration_ms,
            "client_ip": client_ip,
            "user_id": user_id,
        }

        # Registrar en el log estándar en formato JSON de una sola línea
        try:
            logger.info(json.dumps(metric_data, ensure_ascii=False))
        except Exception:
            # Fallback seguro para evitar interrumpir la respuesta del servidor
            logger.info(json.dumps({
                "type": "api_metric",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "method": request.method,
                "path": request.path,
                "status_code": status_code,
                "status_class": status_class,
                "duration_ms": duration_ms
            }))

        return response
