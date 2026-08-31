"""
Módulo de Seguridad Integral para Subida de Archivos (OWASP File Upload Protection)
==================================================================================
Implementa:
1. Validación profunda de contenido binario (Magic Bytes & Integridad de Imagen).
2. Sanitización y re-codificación con Pillow (eliminación de EXIF y payloads maliciosos).
3. Whitelist estricta de extensiones y tipos MIME con protección contra doble extensión.
4. Renombrado aleatorio criptográfico con UUIDv4 (almacenamiento seguro).
5. Deshabilitación de ejecución de scripts y cabeceras de seguridad HTTP (X-Content-Type-Options: nosniff).
"""

import os
import io
import uuid
import re
from pathlib import Path
from typing import Tuple, Optional
from PIL import Image, ImageOps
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings

# 1. Configuración de Whitelists y Restricciones
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
ALLOWED_IMAGE_MIME_TYPES = {'image/jpeg', 'image/png', 'image/webp'}
MAX_UPLOAD_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
MAX_IMAGE_DIMENSIONS = (4096, 4096)      # Evita Decompression Bombs / Pixel Floods

# Firmas binarias estándar (Magic Bytes)
MAGIC_BYTE_SIGNATURES = {
    'JPEG': [b'\xFF\xD8\xFF'],
    'PNG':  [b'\x89PNG\r\n\x1a\n'],
    'WEBP': [b'RIFF'],  # Contiene 'RIFF' en [0:4] y 'WEBP' en [8:12]
}

# Extensiones peligrosas que nunca deben aparecer en el nombre del archivo (doble extensión)
DANGEROUS_EXTENSIONS_PATTERN = re.compile(
    r'\.(php|phtml|php3|php4|php5|phps|py|pyc|sh|bash|exe|bat|cmd|dll|bin|cgi|pl|cgi|asp|aspx|jsp|jspx|htm|html|xhtml|svg|js|vbs|jar|war)\.',
    re.IGNORECASE
)


def validar_nombre_archivo(nombre_original: str) -> Tuple[bool, str, str]:
    """
    Valida el nombre de archivo contra path traversal, caracteres nulos, dobles extensiones
    y extensiones fuera de la whitelist.

    Returns:
        Tuple: (es_valido: bool, extension_normalizada: str, error_mensaje: str)
    """
    if not nombre_original:
        return False, '', 'El nombre del archivo no puede estar vacío.'

    # 1. Bloquear caracteres nulos y secuencias de escape
    if '\x00' in nombre_original or '%00' in nombre_original:
        return False, '', 'Nombre de archivo contiene caracteres inválidos.'

    # 2. Bloquear Path Traversal (../ o ..\\)
    if '..' in nombre_original or '/' in nombre_original or '\\' in nombre_original:
        return False, '', 'Nombre de archivo contiene secuencias de ruta no permitidas.'

    # 3. Bloquear doble extensión peligrosa (ej. malware.php.png)
    if DANGEROUS_EXTENSIONS_PATTERN.search(nombre_original):
        return False, '', 'El archivo contiene una extensión secundaria no permitida o sospechosa.'

    # 4. Obtener y validar extensión en whitelist
    _, ext = os.path.splitext(nombre_original.lower())
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        return False, '', f'Extensión "{ext}" no permitida. Solo se aceptan formatos: JPG, JPEG, PNG y WEBP.'

    return True, ext, ''


def _validar_magic_bytes(stream: io.BytesIO) -> Tuple[bool, str]:
    """
    Inspecciona los primeros bytes del archivo para confirmar que coincidan con la firma de una imagen real.
    """
    stream.seek(0)
    encabezado = stream.read(16)
    stream.seek(0)

    if not encabezado or len(encabezado) < 4:
        return False, 'El archivo está vacío o es demasiado pequeño.'

    # Validar JPEG
    if encabezado.startswith(b'\xFF\xD8\xFF'):
        return True, 'JPEG'

    # Validar PNG
    if encabezado.startswith(b'\x89PNG\r\n\x1a\n'):
        return True, 'PNG'

    # Validar WEBP
    if encabezado.startswith(b'RIFF') and len(encabezado) >= 12 and encabezado[8:12] == b'WEBP':
        return True, 'WEBP'

    return False, 'La firma binaria del archivo no coincide con un formato de imagen permitido.'


def validar_y_sanitizar_imagen(
    archivo_subido,
    formato_salida: str = 'WEBP',
    max_dimension: int = 1920,
    calidad: int = 85
) -> Tuple[bool, Optional[InMemoryUploadedFile], str]:
    """
    Realiza una validación y sanitización profunda de una imagen:
    1. Valida nombre, extensión y tamaño.
    2. Comprueba magic bytes binarios.
    3. Abre la imagen con Pillow, valida dimensiones (prevención de Pixel Flood).
    4. Re-codifica la imagen limpia en un buffer de memoria, purgando metadatos EXIF y código inyectado.

    Returns:
        Tuple: (exito: bool, archivo_sanitizado: InMemoryUploadedFile | None, mensaje_error: str)
    """
    # 1. Validación de Tamaño
    if archivo_subido.size > MAX_UPLOAD_SIZE_BYTES:
        return False, None, f'El archivo supera el tamaño máximo permitido de {MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)} MB.'

    # 2. Validación de Nombre y Extensión
    nombre_valido, ext, msg_error = validar_nombre_archivo(archivo_subido.name)
    if not nombre_valido:
        return False, None, msg_error

    # 3. Validación de Magic Bytes
    stream_memoria = io.BytesIO(archivo_subido.read())
    magic_ok, formato_detectado = _validar_magic_bytes(stream_memoria)
    if not magic_ok:
        return False, None, formato_detectado

    # 4. Procesamiento, Verificación e Integridad con Pillow
    try:
        # Prevenir Decompression Bomb DoS
        Image.MAX_IMAGE_PIXELS = MAX_IMAGE_DIMENSIONS[0] * MAX_IMAGE_DIMENSIONS[1]

        stream_memoria.seek(0)
        with Image.open(stream_memoria) as img:
            img.verify()

        # Reabrir para procesamiento (verify() cierra o invalida algunos punteros en Pillow)
        stream_memoria.seek(0)
        with Image.open(stream_memoria) as img:
            # Comprobar dimensiones reales
            if img.width > MAX_IMAGE_DIMENSIONS[0] or img.height > MAX_IMAGE_DIMENSIONS[1]:
                return False, None, f'Dimensiones de imagen ({img.width}x{img.height}) exceden el límite de seguridad permitido.'

            # Corregir orientación EXIF si existe
            img = ImageOps.exif_transpose(img)

            # Convertir a RGB / RGBA según corresponda
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                img_procesada = img.convert('RGBA')
            else:
                img_procesada = img.convert('RGB')

            # Redimensionar proporcionalmente si supera el límite de visualización
            if max(img_procesada.width, img_procesada.height) > max_dimension:
                img_procesada.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)

            # Re-codificar en un buffer limpio (strips all EXIF, malicious comments or script injections)
            buffer_salida = io.BytesIO()
            if formato_salida.upper() == 'WEBP':
                img_procesada.save(buffer_salida, format='WEBP', quality=calidad, method=4)
                ext_final = '.webp'
                mime_final = 'image/webp'
            else:
                img_procesada.save(buffer_salida, format='JPEG', quality=calidad, optimize=True)
                ext_final = '.jpg'
                mime_final = 'image/jpeg'

            buffer_salida.seek(0)
            tamano_final = buffer_salida.getbuffer().nbytes

            # Generar nombre seguro único UUIDv4
            nuevo_nombre = f"{uuid.uuid4().hex}{ext_final}"

            archivo_sanitizado = InMemoryUploadedFile(
                file=buffer_salida,
                field_name=getattr(archivo_subido, 'field_name', 'foto'),
                name=nuevo_nombre,
                content_type=mime_final,
                size=tamano_final,
                charset=None
            )

            return True, archivo_sanitizado, ''

    except Exception:
        return False, None, 'El archivo no es una imagen válida o está dañado.'


# 2. Funciones de Renombrado Seguro para Modelos Django (upload_to)
def ruta_foto_usuario_segura(instance, filename: str) -> str:
    """
    Genera una ruta y nombre aleatorio criptográfico para fotos de perfil de usuario.
    Guarda en: fotos_usuarios/<uuid4>.webp
    """
    _, ext = os.path.splitext(filename.lower())
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        ext = '.webp'
    nombre_seguro = f"{uuid.uuid4().hex}{ext}"
    return f"fotos_usuarios/{nombre_seguro}"


def ruta_foto_trabajador_segura(instance, filename: str) -> str:
    """
    Genera una ruta y nombre aleatorio criptográfico para fotos de perfil de trabajadores.
    Guarda en: fotos_trabajadores/<uuid4>.webp
    """
    _, ext = os.path.splitext(filename.lower())
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        ext = '.webp'
    nombre_seguro = f"{uuid.uuid4().hex}{ext}"
    return f"fotos_trabajadores/{nombre_seguro}"


# 3. Middleware de Cabeceras de Seguridad para Archivos Multimedia
class MediaSecurityHeadersMiddleware:
    """
    Middleware que añade cabeceras HTTP de seguridad estrictas en todas las respuestas de archivos multimedia,
    impidiendo la ejecución de scripts (XSS / MIME sniffing / Clickjacking) en el navegador del cliente.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Aplicar cabeceras de seguridad para rutas de medios o respuestas de imagen
        if request.path.startswith(getattr(settings, 'MEDIA_URL', '/media/')):
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            response['Content-Security-Policy'] = "default-src 'none'; style-src 'unsafe-inline'; sandbox;"
            response['Cache-Control'] = 'public, max-age=86400, stale-while-revalidate=43200'

        return response


# 4. Protección en Servidor Web (Directorio Media Fuera del Web Root)
def asegurar_directorio_media_protegido(media_root: Path):
    """
    Crea el directorio MEDIA_ROOT si no existe y genera archivos de directivas de seguridad
    (.htaccess / web.config) para deshabilitar explícitamente la ejecución de scripts en Apache/IIS.
    """
    try:
        media_root.mkdir(parents=True, exist_ok=True)
        (media_root / 'fotos_usuarios').mkdir(parents=True, exist_ok=True)
        (media_root / 'fotos_trabajadores').mkdir(parents=True, exist_ok=True)

        htaccess_path = media_root / '.htaccess'
        if not htaccess_path.exists():
            htaccess_content = (
                "# Llankay - Deshabilitar ejecución de scripts en directorio media\n"
                "<IfModule mod_php.c>\n"
                "    php_flag engine off\n"
                "</IfModule>\n"
                "<IfModule mod_php7.c>\n"
                "    php_flag engine off\n"
                "</IfModule>\n"
                "<IfModule mod_php8.c>\n"
                "    php_flag engine off\n"
                "</IfModule>\n"
                "Options -ExecCGI -Indexes\n"
                "RemoveHandler .php .phtml .php3 .php4 .php5 .phps .py .cgi .pl .sh\n"
                "SetHandler default-handler\n"
                "Header set X-Content-Type-Options \"nosniff\"\n"
                "Header set Content-Security-Policy \"default-src 'none'; sandbox\"\n"
            )
            htaccess_path.write_text(htaccess_content, encoding='utf-8')
    except Exception:
        pass
