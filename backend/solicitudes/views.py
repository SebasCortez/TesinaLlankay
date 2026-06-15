from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Solicitud
from .serializers import SolicitudSerializer, SolicitudCrearSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_solicitud(request):
    if request.user.rol != 'cliente':
        return Response({'error': 'Solo clientes pueden enviar solicitudes'}, status=403)
    serializer = SolicitudCrearSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(cliente=request.user)
        return Response({'mensaje': 'Solicitud enviada correctamente'}, status=201)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mis_solicitudes(request):
    if request.user.rol == 'cliente':
        solicitudes = Solicitud.objects.filter(cliente=request.user).order_by('-fecha_solicitud')
    elif request.user.rol == 'trabajador':
        solicitudes = Solicitud.objects.filter(trabajador__usuario=request.user).order_by('-fecha_solicitud')
    else:
        solicitudes = Solicitud.objects.all().order_by('-fecha_solicitud')
    serializer = SolicitudSerializer(solicitudes, many=True)
    return Response(serializer.data)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def actualizar_estado(request, pk):
    try:
        solicitud = Solicitud.objects.get(pk=pk)
    except Solicitud.DoesNotExist:
        return Response({'error': 'No encontrado'}, status=404)

    nuevo_estado = request.data.get('estado')
    motivo = request.data.get('motivo_rechazo', '')

    # Validar permisos por rol
    if request.user.rol == 'trabajador':
        if solicitud.trabajador.usuario != request.user:
            return Response({'error': 'Sin permisos'}, status=403)
        if nuevo_estado not in ['aceptado', 'rechazado', 'en_progreso', 'completado']:
            return Response({'error': 'Estado no válido'}, status=400)

    elif request.user.rol == 'cliente':
        if solicitud.cliente != request.user:
            return Response({'error': 'Sin permisos'}, status=403)
        if nuevo_estado not in ['completado']:
            return Response({'error': 'Estado no válido'}, status=400)

    solicitud.estado = nuevo_estado
    if motivo:
        solicitud.motivo_rechazo = motivo
    solicitud.save()
    return Response({'mensaje': f'Solicitud actualizada a {nuevo_estado}'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_listar_solicitudes(request):
    if request.user.rol != 'admin':
        return Response({'error': 'Sin permisos'}, status=403)
    solicitudes = Solicitud.objects.all().order_by('-fecha_solicitud')
    serializer = SolicitudSerializer(solicitudes, many=True)
    return Response(serializer.data)