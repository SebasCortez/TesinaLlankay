import random
import time
import hmac
import hashlib
import base64
import html
from django.conf import settings
from typing import Dict, Any, Tuple

CAPTCHA_TIMEOUT_SECONDS = 180  # 3 minutos de validez


def _generar_firma_hmac(texto_respuesta: str, timestamp: int, salt: str) -> str:
    """
    Genera una firma criptográfica HMAC-SHA256 para el captcha.
    """
    secret = getattr(settings, 'SECRET_KEY', 'default-captcha-secret-key-2026')
    mensaje = f"{texto_respuesta.strip().lower()}:{timestamp}:{salt}"
    firma = hmac.new(secret.encode('utf-8'), mensaje.encode('utf-8'), hashlib.sha256).hexdigest()
    return firma


def generar_captcha_reto() -> Dict[str, Any]:
    """
    Genera un reto CAPTCHA visual / aritmético en formato SVG seguro con firma cifrada.

    Returns:
        Dict con:
        {
            "captcha_key": str (token firmado con timestamp y salt),
            "svg_image": str (código SVG de la imagen del captcha),
            "tipo": "aritmetico" | "alfanumerico"
        }
    """
    salt = hex(random.randint(100000, 999999))[2:]
    timestamp = int(time.time())

    # Generar reto aritmético (ej. "8 + 5", "14 - 6", "7 + 9")
    operacion = random.choice(['+', '-'])
    if operacion == '+':
        num1 = random.randint(3, 15)
        num2 = random.randint(2, 12)
        resultado = num1 + num2
        texto_desafio = f"{num1} + {num2} = ?"
    else:
        num1 = random.randint(10, 25)
        num2 = random.randint(1, 9)
        resultado = num1 - num2
        texto_desafio = f"{num1} - {num2} = ?"

    respuesta_correcta = str(resultado)

    # Generar firma HMAC
    firma = _generar_firma_hmac(respuesta_correcta, timestamp, salt)

    # El captcha_key empaqueta timestamp, salt y firma
    payload = f"{timestamp}:{salt}:{firma}"
    captcha_key = base64.urlsafe_b64encode(payload.encode('utf-8')).decode('utf-8')

    # Generar SVG visualmente atractivo con ruido anti-bot
    ancho = 200
    alto = 60
    lineas_ruido = ""
    for _ in range(4):
        x1, y1 = random.randint(0, ancho), random.randint(0, alto)
        x2, y2 = random.randint(0, ancho), random.randint(0, alto)
        color = random.choice(['#6366F1', '#8B5CF6', '#3B82F6', '#A855F7', '#CBD5E1'])
        lineas_ruido += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.5" opacity="0.45" />'

    puntos_ruido = ""
    for _ in range(16):
        cx, cy = random.randint(5, ancho - 5), random.randint(5, alto - 5)
        r = random.randint(1, 3)
        color = random.choice(['#6366F1', '#10B981', '#F59E0B', '#94A3B8'])
        puntos_ruido += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}" opacity="0.4" />'

    # Renderizar cada caracter con ligera rotación y desplazamiento
    svg_caracteres = ""
    inicio_x = 24
    for i, char in enumerate(texto_desafio):
        rotacion = random.randint(-8, 8)
        offset_y = random.randint(-3, 3)
        svg_caracteres += f'<text x="{inicio_x + i * 22}" y="{38 + offset_y}" font-family="Arial, sans-serif" font-size="22" font-weight="bold" fill="#4F46E5" transform="rotate({rotacion}, {inicio_x + i * 22}, 38)">{html.escape(char)}</text>'

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}" viewBox="0 0 {ancho} {alto}" style="border-radius: 8px; background: rgba(79, 70, 229, 0.06); border: 1px solid rgba(79, 70, 229, 0.2);">
        <rect width="100%" height="100%" fill="none" rx="8" />
        {lineas_ruido}
        {puntos_ruido}
        {svg_caracteres}
    </svg>'''

    return {
        "captcha_key": captcha_key,
        "svg_image": svg_content,
        "pregunta": "¿Cuánto es la operación?",
        "expira_en_segundos": CAPTCHA_TIMEOUT_SECONDS
    }


def generar_captcha_para_test(respuesta: str = "42") -> Tuple[str, str]:
    """
    Helper para pruebas automatizadas que genera un par (captcha_key, captcha_value) válido.
    """
    salt = "testsalt123"
    timestamp = int(time.time())
    firma = _generar_firma_hmac(respuesta, timestamp, salt)
    payload = f"{timestamp}:{salt}:{firma}"
    key = base64.urlsafe_b64encode(payload.encode('utf-8')).decode('utf-8')
    return key, respuesta


def validar_captcha(captcha_key: str, respuesta_usuario: str) -> Tuple[bool, str]:
    """
    Valida la respuesta del usuario contra el token de captcha firmado.

    Returns:
        Tuple (es_valido: bool, mensaje_error: str | None)
    """
    if not captcha_key or not respuesta_usuario:
        return False, "Debes completar el código de seguridad CAPTCHA."

    try:
        raw_payload = base64.urlsafe_b64decode(captcha_key.encode('utf-8')).decode('utf-8')
        partes = raw_payload.split(':')
        if len(partes) != 3:
            return False, "Token de CAPTCHA inválido o corrupto."

        timestamp_str, salt, firma_recibida = partes
        timestamp = int(timestamp_str)
        ahora = int(time.time())

        # Validar expiración
        if ahora - timestamp > CAPTCHA_TIMEOUT_SECONDS:
            return False, "El código CAPTCHA ha expirado. Por favor genera uno nuevo."

        if timestamp > ahora + 30:
            return False, "Timestamp de CAPTCHA inválido."

        # Calcular firma esperada con la respuesta ingresada
        firma_esperada = _generar_firma_hmac(str(respuesta_usuario), timestamp, salt)

        if not hmac.compare_digest(firma_esperada, firma_recibida):
            return False, "Respuesta de CAPTCHA incorrecta. Inténtalo nuevamente."

        return True, ""

    except Exception as e:
        return False, "Error al verificar el CAPTCHA."
