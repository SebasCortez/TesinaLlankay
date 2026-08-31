from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db.models import Avg
from drf_spectacular.utils import extend_schema
from .models import Calificacion, CalificacionCliente
from .serializers import (
    CalificacionSerializer,
    CalificacionCrearSerializer,
    CalificacionClienteSerializer,
    CalificacionClienteCrearSerializer
)
from trabajadores.models import Trabajador

@extend_schema(
    summary="Crear calificación para un técnico (Cliente → Técnico)",
    request=CalificacionCrearSerializer,
    responses={201: CalificacionSerializer, 400: dict}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_calificacion(request):
    serializer = CalificacionCrearSerializer(data=request.data)
    if serializer.is_valid():
        trabajador = serializer.validated_data['trabajador']
        solicitud = serializer.validated_data.get('solicitud')

        # No se puede calificar a uno mismo
        if trabajador.usuario == request.user:
            return Response({'error': 'No puedes calificarte a ti mismo.'}, status=status.HTTP_400_BAD_REQUEST)

        # Si se especifica una solicitud, validar que pertenezca al cliente que la solicitó y esté completada
        if solicitud:
            if solicitud.cliente != request.user:
                return Response({'error': 'La solicitud no pertenece a tu usuario.'}, status=status.HTTP_400_BAD_REQUEST)
            if solicitud.estado != 'completado':
                return Response({'error': 'Solo se pueden calificar solicitudes completadas.'}, status=status.HTTP_400_BAD_REQUEST)
            if Calificacion.objects.filter(solicitud=solicitud).exists():
                return Response({'error': 'Esta solicitud ya ha sido calificada.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Si no hay solicitud asociada, mantener regla de una calificación por cliente/técnico
            if Calificacion.objects.filter(trabajador=trabajador, cliente=request.user, solicitud__isnull=True).exists():
                return Response({'error': 'Ya calificaste a este profesional anteriormente.'}, status=status.HTTP_400_BAD_REQUEST)

        calificacion = serializer.save(cliente=request.user)

        # Recalcular promedio de forma eficiente usando agregación ORM
        agg = Calificacion.objects.filter(trabajador=trabajador).aggregate(
            promedio=Avg('puntuacion')
        )
        total_califs = Calificacion.objects.filter(trabajador=trabajador).count()
        trabajador.calificacion_promedio = round(agg['promedio'] or 0.0, 1)
        trabajador.num_calificaciones = total_califs
        trabajador.save()

        # Notificar al técnico
        from notificaciones.models import crear_notificacion
        crear_notificacion(
            usuario=trabajador.usuario,
            titulo="⭐ Nueva Calificación Recibida",
            mensaje=f"{request.user.get_full_name()} te ha calificado con {calificacion.puntuacion} estrellas: \"{calificacion.comentario[:80]}\"",
            tipo="calificacion_recibida",
            enlace=f"/trabajador/{trabajador.id}"
        )

        return Response({
            'mensaje': 'Calificación registrada exitosamente.',
            'calificacion': CalificacionSerializer(calificacion).data
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Listar calificaciones de un técnico",
    responses={200: CalificacionSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def listar_calificaciones(request, trabajador_id):
    calificaciones = Calificacion.objects.filter(
        trabajador_id=trabajador_id
    ).select_related('cliente').order_by('-fecha')
    serializer = CalificacionSerializer(calificaciones, many=True)
    return Response(serializer.data)


@extend_schema(
    summary="Crear calificación para un cliente (Técnico → Cliente)",
    request=CalificacionClienteCrearSerializer,
    responses={201: CalificacionClienteSerializer, 400: dict}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_calificacion_cliente(request):
    """
    Permite al profesional técnico calificar al cliente tras completar una solicitud de servicio.
    """
    trabajador = Trabajador.objects.filter(usuario=request.user).first()
    if not trabajador:
        return Response({'error': 'Solo los técnicos profesionales pueden calificar a clientes.'}, status=status.HTTP_403_FORBIDDEN)

    serializer = CalificacionClienteCrearSerializer(data=request.data)
    if serializer.is_valid():
        cliente = serializer.validated_data['cliente']
        solicitud = serializer.validated_data.get('solicitud')

        # No se puede calificar a uno mismo
        if cliente == request.user:
            return Response({'error': 'No puedes calificarte a ti mismo.'}, status=status.HTTP_400_BAD_REQUEST)

        if not solicitud:
            return Response({'error': 'Debes asociar la calificación a una solicitud de servicio.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validar que la solicitud corresponda al técnico y cliente
        if solicitud.trabajador != trabajador:
            return Response({'error': 'No estás asignado a esta solicitud de trabajo.'}, status=status.HTTP_400_BAD_REQUEST)
        if solicitud.cliente != cliente:
            return Response({'error': 'El cliente no coincide con la solicitud indicada.'}, status=status.HTTP_400_BAD_REQUEST)
        if solicitud.estado != 'completado':
            return Response({'error': 'Solo puedes calificar solicitudes completadas.'}, status=status.HTTP_400_BAD_REQUEST)
        if CalificacionCliente.objects.filter(solicitud=solicitud).exists():
            return Response({'error': 'Ya has calificado a este cliente por este trabajo.'}, status=status.HTTP_400_BAD_REQUEST)

        calificacion = serializer.save(trabajador=trabajador)

        # Notificar al cliente
        from notificaciones.models import crear_notificacion
        crear_notificacion(
            usuario=cliente,
            titulo="⭐ Nueva Calificación de tu Técnico",
            mensaje=f"{request.user.get_full_name()} ({trabajador.oficio}) te ha calificado con {calificacion.puntuacion} estrellas: \"{calificacion.comentario[:80]}\"",
            tipo="calificacion_cliente_recibida",
            enlace="/solicitudes"
        )

        return Response({
            'mensaje': 'Calificación de cliente registrada exitosamente.',
            'calificacion': CalificacionClienteSerializer(calificacion).data
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Listar calificaciones recibidas por un cliente",
    responses={200: CalificacionClienteSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_calificaciones_cliente(request, cliente_id):
    calificaciones = CalificacionCliente.objects.filter(
        cliente_id=cliente_id
    ).select_related('trabajador__usuario', 'cliente').order_by('-fecha')
    serializer = CalificacionClienteSerializer(calificaciones, many=True)
    return Response(serializer.data)