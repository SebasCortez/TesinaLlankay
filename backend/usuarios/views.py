import os
import requests
from PIL import Image
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from config.throttling import LoginRateThrottle, RegistroRateThrottle, PasswordResetRateThrottle
from .captcha import generar_captcha_reto
from .models import Usuario
from .serializers import (
    RegistroSerializer,
    LoginSerializer,
    UsuarioSerializer,
    ActualizarUsuarioSerializer,
    CambiarPasswordSerializer,
    RecuperarPasswordSerializer,
    RestablecerPasswordSerializer,
    GoogleAuthSerializer
)


@extend_schema(
    summary="Obtener un nuevo desafío CAPTCHA",
    description="Genera un reto visual/aritmético con firma HMAC para proteger el inicio de sesión contra bots.",
    responses={200: dict}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_captcha(request):
    reto = generar_captcha_reto()
    return Response(reto, status=status.HTTP_200_OK)


@extend_schema(
    summary="Registro de nuevo usuario (cliente o trabajador)",
    request=RegistroSerializer,
    responses={201: dict, 400: dict}
)
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([RegistroRateThrottle])
def registro(request):
    serializer = RegistroSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {'mensaje': 'Usuario registrado exitosamente'},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Iniciar sesión y obtener tokens JWT (requiere CAPTCHA)",
    request=LoginSerializer,
    responses={200: dict, 400: dict}
)
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([LoginRateThrottle])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        return Response(serializer.validated_data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Solicitar enlace de recuperación de contraseña por correo",
    request=RecuperarPasswordSerializer,
    responses={200: dict, 400: dict}
)
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([PasswordResetRateThrottle])
def recuperar_password(request):
    serializer = RecuperarPasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email'].strip().lower()
    user = Usuario.objects.filter(email__iexact=email).first()

    if user:
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        reset_link = f"{frontend_url}/restablecer-password?uid={uid}&token={token}"

        asunto = "Restablece tu contraseña - TécniCusco"
        mensaje = (
            f"Hola {user.first_name or user.username},\n\n"
            f"Hemos recibido una solicitud para restablecer la contraseña de tu cuenta en TécniCusco.\n\n"
            f"Haz clic en el siguiente enlace o cópialo en tu navegador para continuar:\n"
            f"{reset_link}\n\n"
            f"Este enlace es válido por tiempo limitado. Si no realizaste esta solicitud, puedes ignorar este mensaje.\n\n"
            f"Atentamente,\n"
            f"El equipo de TécniCusco (Tesina Llankay)"
        )
        try:
            send_mail(
                asunto,
                mensaje,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False
            )
        except Exception as e:
            print(f"[Aviso] Error al enviar email: {e}")
            print(f"[Enlace de recuperación generado]: {reset_link}")

    return Response({
        'mensaje': 'Si el correo electrónico está registrado en TécniCusco, recibirás un enlace con instrucciones para restablecer tu contraseña.'
    }, status=status.HTTP_200_OK)

@extend_schema(
    summary="Restablecer contraseña usando token y uid",
    request=RestablecerPasswordSerializer,
    responses={200: dict, 400: dict}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def restablecer_password(request):
    serializer = RestablecerPasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    uid = serializer.validated_data['uid']
    token = serializer.validated_data['token']
    password = serializer.validated_data['password']

    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = Usuario.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        return Response({'error': 'El enlace de recuperación es inválido o no existe.'}, status=status.HTTP_400_BAD_REQUEST)

    if not default_token_generator.check_token(user, token):
        return Response({'error': 'El enlace de recuperación ha expirado o ya fue utilizado.'}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(password)
    user.save()

    return Response({
        'mensaje': 'Tu contraseña ha sido restablecida exitosamente. Ya puedes iniciar sesión con tu nueva contraseña.'
    }, status=status.HTTP_200_OK)

@extend_schema(
    summary="Inicio de sesión o registro automático con Google (OAuth 2.0 / GIS)",
    request=GoogleAuthSerializer,
    responses={200: dict, 400: dict}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def google_login(request):
    serializer = GoogleAuthSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    credential = serializer.validated_data['credential']
    google_client_id = getattr(settings, 'GOOGLE_CLIENT_ID', '')

    google_data = None

    # Modo simulación para desarrollo local / pruebas / prototipo
    if credential.startswith('demo-google-token:'):
        email_demo = credential.replace('demo-google-token:', '').strip().lower()
        if '@' in email_demo:
            name_part = email_demo.split('@')[0].replace('.', ' ').title()
            google_data = {
                'email': email_demo,
                'given_name': name_part.split(' ')[0] if ' ' in name_part else name_part,
                'family_name': name_part.split(' ')[1] if ' ' in name_part else '',
                'name': name_part
            }


    if not google_data:
        # Intento 1: Verificar con google-auth si hay client_id o token estándar
        try:
            google_data = id_token.verify_oauth2_token(
                credential,
                google_requests.Request(),
                google_client_id if google_client_id else None
            )
        except Exception:
            # Intento 2: Consultar directamente el endpoint tokeninfo de Google
            try:
                resp = requests.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={credential}", timeout=5)
                if resp.status_code == 200:
                    google_data = resp.json()
            except Exception as e:
                print(f"Error al validar token de Google: {e}")

    if not google_data or 'email' not in google_data:
        return Response({'error': 'El token de Google no es válido o ha expirado.'}, status=status.HTTP_400_BAD_REQUEST)

    email = google_data['email'].strip().lower()
    first_name = google_data.get('given_name') or google_data.get('name', 'Usuario')
    last_name = google_data.get('family_name', '')

    # Buscar usuario por email
    user = Usuario.objects.filter(email__iexact=email).first()

    if not user:
        # Generar username único
        base_username = email.split('@')[0].replace('.', '_').replace('-', '_')
        username = base_username
        contador = 1
        while Usuario.objects.filter(username=username).exists():
            username = f"{base_username}_{contador}"
            contador += 1

        user = Usuario.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            rol='cliente',
            distrito='Cusco'
        )

    tokens = RefreshToken.for_user(user)
    return Response({
        'access': str(tokens.access_token),
        'refresh': str(tokens),
        'usuario': UsuarioSerializer(user, context={'request': request}).data
    }, status=status.HTTP_200_OK)

@extend_schema(
    summary="Obtener perfil del usuario autenticado",
    responses={200: UsuarioSerializer}
)
@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def perfil(request):
    if request.method == 'PATCH':
        serializer = ActualizarUsuarioSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'mensaje': 'Perfil actualizado correctamente.',
                'usuario': UsuarioSerializer(request.user, context={'request': request}).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer = UsuarioSerializer(request.user, context={'request': request})
    return Response(serializer.data)

@extend_schema(
    summary="Subir o actualizar foto de perfil del usuario de forma segura",
    responses={200: dict, 400: dict}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subir_foto_usuario(request):
    if 'foto' not in request.FILES:
        return Response({'error': 'No se proporcionó ningún archivo de imagen.'}, status=status.HTTP_400_BAD_REQUEST)

    foto = request.FILES['foto']

    # 1. Validación de tamaño (Máx 5MB)
    if foto.size > 5 * 1024 * 1024:
        return Response({'error': 'La imagen no debe superar los 5 MB.'}, status=status.HTTP_400_BAD_REQUEST)

    # 2. Validación de extensión
    ext = os.path.splitext(foto.name)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
        return Response({'error': 'Formato no permitido. Solo se aceptan imágenes JPG, PNG o WEBP.'}, status=status.HTTP_400_BAD_REQUEST)

    # 3. Validación de contenido con Pillow (Magic Bytes / Integrity Check)
    try:
        img = Image.open(foto)
        img.verify()
        foto.seek(0)
    except Exception:
        return Response({'error': 'El archivo subido no es una imagen válida o está dañado.'}, status=status.HTTP_400_BAD_REQUEST)

    # Guardar en modelo Usuario
    request.user.foto = foto
    request.user.save()

    # Si es técnico, sincronizar también en su perfil técnico
    if hasattr(request.user, 'perfil_trabajador'):
        request.user.perfil_trabajador.foto = request.user.foto
        request.user.perfil_trabajador.save()

    foto_url = request.build_absolute_uri(request.user.foto.url)
    return Response({
        'mensaje': 'Foto de perfil actualizada exitosamente.',
        'foto_url': foto_url,
        'usuario': UsuarioSerializer(request.user, context={'request': request}).data
    }, status=status.HTTP_200_OK)

@extend_schema(
    summary="Cambiar contraseña de usuario autenticado",
    request=CambiarPasswordSerializer,
    responses={200: dict, 400: dict}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cambiar_password(request):
    serializer = CambiarPasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    password_actual = serializer.validated_data['password_actual']
    password_nueva = serializer.validated_data['password_nueva']

    if not request.user.check_password(password_actual):
        return Response({'error': 'La contraseña actual ingresada es incorrecta.'}, status=status.HTTP_400_BAD_REQUEST)

    if password_actual == password_nueva:
        return Response({'error': 'La nueva contraseña no puede ser igual a la anterior.'}, status=status.HTTP_400_BAD_REQUEST)

    request.user.set_password(password_nueva)
    request.user.save()

    return Response({
        'mensaje': 'Contraseña cambiada exitosamente.'
    }, status=status.HTTP_200_OK)

@extend_schema(
    summary="[Admin] Listar todos los clientes",
    responses={200: UsuarioSerializer(many=True), 403: dict}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_listar_clientes(request):
    if request.user.rol != 'admin':
        return Response({'error': 'Sin permisos'}, status=status.HTTP_403_FORBIDDEN)
    clientes = Usuario.objects.filter(rol='cliente')
    serializer = UsuarioSerializer(clientes, many=True, context={'request': request})
    return Response(serializer.data)