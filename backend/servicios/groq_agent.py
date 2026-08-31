"""
Módulo de Integración con Groq API para Agentes Conversacionales en Django
========================================================================
Utiliza el SDK oficial de OpenAI configurado con el endpoint de inferencia ultrarrápida
de Groq (https://api.groq.com/openai/v1) y el modelo LLaMA 3.3 70B Versatile.
"""

import os
import logging
import time
from typing import List, Dict, Any, Optional
from openai import (
    OpenAI,
    APITimeoutError,
    RateLimitError,
    APIConnectionError,
    AuthenticationError,
    APIStatusError,
    NotFoundError,
    OpenAIError
)

from pathlib import Path
from dotenv import load_dotenv
from django.conf import settings

logger = logging.getLogger('servicios.groq_agent')

# Configuración predeterminada
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
GROQ_DEFAULT_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
GROQ_FALLBACK_MODELS = ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b", "qwen/qwen3.6-27b"]
DEFAULT_TIMEOUT_SECONDS = float(os.getenv("GROQ_TIMEOUT", "25.0"))


def _obtener_groq_api_key() -> str:
    """
    Obtiene la clave de Groq desde settings de Django, os.environ o recargando el .env en caliente.
    """
    # 1. Intentar desde settings de Django si están configurados
    if settings.configured and hasattr(settings, 'GROQ_API_KEY') and settings.GROQ_API_KEY:
        return settings.GROQ_API_KEY

    # 2. Intentar desde os.environ
    key = os.getenv("GROQ_API_KEY", "").strip()
    if key:
        return key

    # 3. Si aún está vacía, recargar .env en caliente
    base_dir = (getattr(settings, 'BASE_DIR', None) if settings.configured else None) or Path(__file__).resolve().parent.parent
    env_path = Path(base_dir) / '.env'
    if env_path.exists():
        load_dotenv(env_path, override=True)
        key = os.getenv("GROQ_API_KEY", "").strip()
        if key:
            return key

    return ""


def obtener_cliente_groq(
    api_key: Optional[str] = None,
    timeout: float = DEFAULT_TIMEOUT_SECONDS
) -> OpenAI:
    """
    Crea y retorna una instancia del cliente OpenAI apuntando al endpoint de Groq.
    
    Args:
        api_key: Clave de API de Groq (opcional, por defecto lee de GROQ_API_KEY).
        timeout: Tiempo máximo de espera en segundos para las solicitudes HTTP.
        
    Returns:
        Instancia de openai.OpenAI configurada para Groq.
    """
    key = api_key or _obtener_groq_api_key()
    if not key:
        logger.warning(
            "GROQ_API_KEY no está configurada. Por favor define GROQ_API_KEY en tu archivo .env o en el entorno."
        )

    base_url = (getattr(settings, 'GROQ_BASE_URL', None) if settings.configured else None) or os.getenv("GROQ_BASE_URL", GROQ_BASE_URL)

    return OpenAI(
        base_url=base_url,
        api_key=key if key else "dummy_key_not_configured",
        timeout=timeout
    )



def generar_respuesta_agente(
    system_prompt: str,
    historial: List[Dict[str, str]],
    modelo: str = GROQ_DEFAULT_MODEL,
    temperatura: float = 0.7,
    max_tokens: int = 1024,
    cliente: Optional[OpenAI] = None,
    max_reintentos_rate_limit: int = 1,
    segundos_espera_reintento: float = 2.0
) -> Dict[str, Any]:
    """
    Envía el system prompt y el historial de turnos al agente en Groq
    y devuelve la respuesta generada con manejo estructurado de errores y timeouts.

    Args:
        system_prompt: Instrucciones base de comportamiento del agente (rol, contexto, reglas).
        historial: Lista de mensajes previos en formato [{"role": "user"|"assistant", "content": "..."}].
        modelo: Identificador del modelo en Groq (por defecto: 'llama-3.3-70b-versatile').
        temperatura: Grado de creatividad/determinismo (0.0 a 1.0).
        max_tokens: Límite máximo de tokens de salida.
        cliente: Instancia personalizada de OpenAI (opcional).
        max_reintentos_rate_limit: Cantidad de reintentos automáticos si ocurre RateLimitError.
        segundos_espera_reintento: Segundos de pausa antes de reintentar ante un RateLimitError.

    Returns:
        Diccionario con la siguiente estructura:
        {
            "exito": True | False,
            "respuesta": "Texto de la respuesta..." | None,
            "error": "Mensaje de error descriptivo..." | None,
            "tipo_error": "rate_limit" | "timeout" | "auth" | "connection" | "api_error" | None,
            "uso": {
                "prompt_tokens": int,
                "completion_tokens": int,
                "total_tokens": int
            } | None,
            "modelo": str
        }
    """
    # Validar o inicializar cliente
    client = cliente or obtener_cliente_groq()

    # Construir la lista completa de mensajes para chat completion
    mensajes = [{"role": "system", "content": system_prompt}]
    
    # Sanitizar y anexar historial de turnos
    for turno in historial:
        if isinstance(turno, dict) and "role" in turno and "content" in turno:
            mensajes.append({
                "role": turno["role"],
                "content": str(turno["content"])
            })

    intentos = 0
    modelos_a_probar = [modelo] + [m for m in GROQ_FALLBACK_MODELS if m != modelo]
    modelo_actual = modelo

    for m in modelos_a_probar:
        try:
            inicio = time.perf_counter()
            response = client.chat.completions.create(
                model=m,
                messages=mensajes,
                temperature=temperatura,
                max_tokens=max_tokens
            )
            latencia_ms = round((time.perf_counter() - inicio) * 1000, 2)
            logger.info(f"Respuesta generada por Groq ({m}) en {latencia_ms}ms.")

            mensaje_generado = response.choices[0].message.content
            uso = None
            if hasattr(response, 'usage') and response.usage:
                uso = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }

            return {
                "exito": True,
                "respuesta": mensaje_generado,
                "error": None,
                "tipo_error": None,
                "uso": uso,
                "modelo": m
            }

        except NotFoundError as e:
            logger.warning(f"El modelo '{m}' no está disponible actualmente en Groq. Probando modelo alternativo...")
            continue

        except RateLimitError as e:
            intentos += 1
            logger.warning(
                f"Límite de tasa (Rate Limit / TPM / RPM) alcanzado en Groq (intento {intentos}/{max_reintentos_rate_limit + 1}): {e}"
            )
            if intentos <= max_reintentos_rate_limit:
                time.sleep(segundos_espera_reintento)
                continue

            return {
                "exito": False,
                "respuesta": None,
                "error": "Se ha superado el límite de solicitudes por minuto de la API de Groq. Por favor intenta nuevamente en unos segundos.",
                "tipo_error": "rate_limit",
                "uso": None,
                "modelo": m
            }


        except APITimeoutError as e:
            logger.error(f"Timeout al conectar con la API de Groq: {e}")
            return {
                "exito": False,
                "respuesta": None,
                "error": "El servicio de Groq tardó demasiado en responder (timeout). Por favor reintenta la consulta.",
                "tipo_error": "timeout",
                "uso": None,
                "modelo": modelo
            }

        except AuthenticationError as e:
            logger.error(f"Error de autenticación con la API Key de Groq: {e}")
            return {
                "exito": False,
                "respuesta": None,
                "error": "Clave de API de Groq inválida o no autorizada. Verifica tu variable GROQ_API_KEY.",
                "tipo_error": "auth",
                "uso": None,
                "modelo": modelo
            }

        except APIConnectionError as e:
            logger.error(f"Error de conexión de red hacia api.groq.com: {e}")
            return {
                "exito": False,
                "respuesta": None,
                "error": "No se pudo establecer conexión de red con los servidores de Groq. Verifica tu conexión a internet.",
                "tipo_error": "connection",
                "uso": None,
                "modelo": modelo
            }

        except (APIStatusError, OpenAIError, Exception) as e:
            logger.error(f"Error inesperado al generar respuesta con Groq: {e}", exc_info=True)
            return {
                "exito": False,
                "respuesta": None,
                "error": f"Error al procesar la solicitud con el agente: {str(e)}",
                "tipo_error": "api_error",
                "uso": None,
                "modelo": modelo
            }
