from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import Notificacion
from .serializers import NotificacionSerializer

@extend_schema(
    summary="Listar notificaciones del usuario autenticado y conteo de no leídas",
    responses={200: dict}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_notificaciones(request):
    notificaciones = Notificacion.objects.filter(usuario=request.user)[:30]
    no_leidas = Notificacion.objects.filter(usuario=request.user, leida=False).count()
    serializer = NotificacionSerializer(notificaciones, many=True)
    return Response({
        'no_leidas': no_leidas,
        'notificaciones': serializer.data
    })

@extend_schema(
    summary="Marcar una notificación individual como leída",
    responses={200: dict, 404: dict}
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def marcar_leida(request, pk):
    try:
        notif = Notificacion.objects.get(pk=pk, usuario=request.user)
        notif.leida = True
        notif.save()
        return Response({'mensaje': 'Notificación marcada como leída.'})
    except Notificacion.DoesNotExist:
        return Response({'error': 'Notificación no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

@extend_schema(
    summary="Marcar todas las notificaciones del usuario como leídas",
    responses={200: dict}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def marcar_todas_leidas(request):
    Notificacion.objects.filter(usuario=request.user, leida=False).update(leida=True)
    return Response({'mensaje': 'Todas las notificaciones fueron marcadas como leídas.'})
