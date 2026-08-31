from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from config.throttling import SolicitudRateThrottle
from .models import Solicitud
from .serializers import SolicitudSerializer, SolicitudCrearSerializer
from trabajadores.models import Trabajador
from notificaciones.models import crear_notificacion

@extend_schema(
    summary="Crear una nueva solicitud de servicio",
    request=SolicitudCrearSerializer,
    responses={201: dict, 400: dict, 404: dict}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([SolicitudRateThrottle])
def crear_solicitud(request):
    serializer = SolicitudCrearSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    trabajador = serializer.validated_data['trabajador']

    # Validación de seguridad: Un usuario no puede contratarse a sí mismo
    if trabajador.usuario == request.user:
        return Response({
            'error': 'No puedes enviarte una solicitud de servicio a ti mismo.'
        }, status=status.HTTP_400_BAD_REQUEST)

    solicitud = serializer.save(cliente=request.user)

    # Disparar notificación en vivo al técnico
    crear_notificacion(
        usuario=trabajador.usuario,
        titulo="🛠️ Nueva Solicitud Recibida",
        mensaje=f"{request.user.get_full_name()} necesita tu servicio de {trabajador.oficio} en {solicitud.direccion}.",
        tipo="solicitud_nueva",
        enlace="/solicitudes"
    )

    return Response({'mensaje': 'Solicitud enviada correctamente', 'id': solicitud.id}, status=status.HTTP_201_CREATED)

@extend_schema(
    summary="Listar solicitudes del usuario actual (enviadas o recibidas)",
    parameters=[
        OpenApiParameter('tipo', str, description="Filtrar por 'enviadas' (como cliente) o 'recibidas' (como técnico)")
    ],
    responses={200: SolicitudSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mis_solicitudes(request):
    tipo = request.query_params.get('tipo')

    if tipo == 'recibidas':
        solicitudes = Solicitud.objects.filter(
            trabajador__usuario=request.user
        ).select_related('trabajador__usuario', 'cliente').order_by('-fecha_solicitud')
    elif tipo == 'enviadas':
        solicitudes = Solicitud.objects.filter(
            cliente=request.user
        ).select_related('trabajador__usuario', 'cliente').order_by('-fecha_solicitud')
    else:
        if request.user.rol == 'admin':
            solicitudes = Solicitud.objects.all().select_related('trabajador__usuario', 'cliente').order_by('-fecha_solicitud')
        elif hasattr(request.user, 'perfil_trabajador') and request.user.rol == 'trabajador':
            solicitudes = Solicitud.objects.filter(
                trabajador__usuario=request.user
            ).select_related('trabajador__usuario', 'cliente').order_by('-fecha_solicitud')
        else:
            solicitudes = Solicitud.objects.filter(
                cliente=request.user
            ).select_related('trabajador__usuario', 'cliente').order_by('-fecha_solicitud')

    serializer = SolicitudSerializer(solicitudes, many=True)
    return Response(serializer.data)

@extend_schema(
    summary="Actualizar estado, cotización o presupuesto de una solicitud",
    responses={200: dict, 400: dict, 403: dict, 404: dict}
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def actualizar_estado(request, pk):
    try:
        solicitud = Solicitud.objects.get(pk=pk)
    except Solicitud.DoesNotExist:
        return Response({'error': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)

    nuevo_estado = request.data.get('estado')
    motivo = request.data.get('motivo_rechazo', '')
    precio_acordado = request.data.get('precio_acordado')
    metodo_pago = request.data.get('metodo_pago')

    es_tecnico_asignado = (solicitud.trabajador.usuario == request.user)
    es_cliente_solicitante = (solicitud.cliente == request.user)
    es_admin = (request.user.rol == 'admin')

    if not (es_tecnico_asignado or es_cliente_solicitante or es_admin):
        return Response({'error': 'No tienes permisos para modificar esta solicitud.'}, status=status.HTTP_403_FORBIDDEN)

    if nuevo_estado:
        if es_tecnico_asignado:
            if nuevo_estado not in ['aceptado', 'rechazado', 'en_progreso', 'completado']:
                return Response({'error': 'Estado no válido para el técnico.'}, status=status.HTTP_400_BAD_REQUEST)
        elif es_cliente_solicitante and not es_admin:
            if nuevo_estado not in ['completado']:
                return Response({'error': 'Como cliente solo puedes marcar la solicitud como completada.'}, status=status.HTTP_400_BAD_REQUEST)
        solicitud.estado = nuevo_estado

    if motivo:
        solicitud.motivo_rechazo = motivo

    if precio_acordado is not None:
        try:
            solicitud.precio_acordado = float(precio_acordado)
        except (ValueError, TypeError):
            pass

    if metodo_pago:
        solicitud.metodo_pago = metodo_pago

    solicitud.save()

    # Disparar notificaciones según cambio de estado
    if nuevo_estado:
        textos_estado = {
            'aceptado': '✅ Tu solicitud fue aceptada por el técnico.',
            'en_progreso': '🔧 El técnico comenzó a trabajar en tu solicitud.',
            'completado': '🎉 El servicio ha sido marcado como completado.',
            'rechazado': f'❌ Tu solicitud no pudo ser atendida. {motivo}'
        }
        destinatario = solicitud.cliente if es_tecnico_asignado else solicitud.trabajador.usuario
        crear_notificacion(
            usuario=destinatario,
            titulo=f"Solicitud {nuevo_estado.replace('_', ' ').capitalize()}",
            mensaje=textos_estado.get(nuevo_estado, f'Estado actualizado a {nuevo_estado}'),
            tipo=f"solicitud_{nuevo_estado}",
            enlace="/solicitudes"
        )

    return Response({
        'mensaje': f'Solicitud actualizada correctamente.',
        'solicitud': SolicitudSerializer(solicitud).data
    })

@extend_schema(
    summary="[Admin] Listar todas las solicitudes del sistema",
    responses={200: SolicitudSerializer(many=True), 403: dict}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_listar_solicitudes(request):
    if request.user.rol != 'admin':
        return Response({'error': 'Sin permisos'}, status=status.HTTP_403_FORBIDDEN)
    solicitudes = Solicitud.objects.all().select_related('trabajador__usuario', 'cliente').order_by('-fecha_solicitud')
    serializer = SolicitudSerializer(solicitudes, many=True)
    return Response(serializer.data)

from .models import RequerimientoOficio
from .serializers import RequerimientoOficioSerializer, RequerimientoOficioCrearSerializer

@extend_schema(
    summary="Crear un requerimiento de oficio no listado (Solo usuarios autenticados)",
    request=RequerimientoOficioCrearSerializer,
    responses={201: dict, 400: dict, 401: dict}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_requerimiento_oficio(request):
    serializer = RequerimientoOficioCrearSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    req = serializer.save(cliente=request.user)

    # Notificación al usuario que registró el pedido
    crear_notificacion(
        usuario=request.user,
        titulo="📌 Requerimiento de Oficio Registrado",
        mensaje=f"Tu pedido para '{req.oficio_solicitado}' en {req.distrito} ha sido registrado. El equipo de soporte se comunicará contigo al {req.celular_contacto}.",
        tipo="sistema",
        enlace="/solicitudes"
    )

    return Response({
        'mensaje': 'Requerimiento registrado con éxito.',
        'id': req.id
    }, status=status.HTTP_201_CREATED)

@extend_schema(
    summary="[Admin] Listar todos los requerimientos de oficios no listados",
    responses={200: RequerimientoOficioSerializer(many=True), 403: dict}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_requerimientos_admin(request):
    if request.user.rol != 'admin' and not request.user.is_staff:
        return Response({'error': 'Acceso no autorizado.'}, status=status.HTTP_403_FORBIDDEN)

    reqs = RequerimientoOficio.objects.all().select_related('cliente').order_by('-fecha_creacion')
    serializer = RequerimientoOficioSerializer(reqs, many=True)
    return Response(serializer.data)

@extend_schema(
    summary="[Admin] Actualizar estado o notas de un requerimiento",
    request=dict,
    responses={200: dict, 403: dict, 404: dict}
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def actualizar_requerimiento_admin(request, pk):
    if request.user.rol != 'admin' and not request.user.is_staff:
        return Response({'error': 'Acceso no autorizado.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        req = RequerimientoOficio.objects.get(pk=pk)
    except RequerimientoOficio.DoesNotExist:
        return Response({'error': 'Requerimiento no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    nuevo_estado = request.data.get('estado')
    notas_admin = request.data.get('notas_admin')

    if nuevo_estado and nuevo_estado in [e[0] for e in RequerimientoOficio.ESTADOS]:
        req.estado = nuevo_estado
    if notas_admin is not None:
        req.notas_admin = notas_admin

    req.save()
    return Response({
        'mensaje': 'Requerimiento actualizado con éxito.',
        'requerimiento': RequerimientoOficioSerializer(req).data
    })