from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.utils import timezone
from math import radians, sin, cos, sqrt, atan2
from .models import Trabajador
from .serializers import TrabajadorSerializer, TrabajadorRegistroSerializer, TrabajadorAdminSerializer

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def registrar_trabajador(request):
    if request.user.rol != 'trabajador':
        return Response({'error': 'Solo usuarios con rol trabajador pueden registrarse'}, status=400)
    if Trabajador.objects.filter(usuario=request.user).exists():
        return Response({'error': 'Ya tienes un perfil de trabajador'}, status=400)
    serializer = TrabajadorRegistroSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(usuario=request.user)
        return Response({'mensaje': 'Solicitud enviada, pendiente de aprobación'}, status=201)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([AllowAny])
def listar_trabajadores(request):
    trabajadores = Trabajador.objects.filter(estado='aprobado')
    categoria = request.query_params.get('categoria')
    busqueda = request.query_params.get('busqueda')
    lat = request.query_params.get('lat')
    lon = request.query_params.get('lon')
    radio = float(request.query_params.get('radio', 5))

    if categoria:
        trabajadores = trabajadores.filter(categoria=categoria)
    if busqueda:
        trabajadores = trabajadores.filter(oficio__icontains=busqueda) | \
                       trabajadores.filter(usuario__first_name__icontains=busqueda)

    resultado = []
    for t in trabajadores:
        data = TrabajadorSerializer(t).data
        if lat and lon and t.latitud and t.longitud:
            distancia = haversine(float(lat), float(lon), t.latitud, t.longitud)
            if distancia <= radio:
                data['distancia_km'] = round(distancia, 1)
                resultado.append(data)
        else:
            data['distancia_km'] = None
            resultado.append(data)

    if lat and lon:
        resultado.sort(key=lambda x: x['distancia_km'] or 999)

    return Response(resultado)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mi_perfil_trabajador(request):
    try:
        trabajador = Trabajador.objects.get(usuario=request.user)
        serializer = TrabajadorSerializer(trabajador)
        return Response(serializer.data)
    except Trabajador.DoesNotExist:
        return Response({'error': 'No tienes perfil de trabajador'}, status=404)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def actualizar_ubicacion(request):
    try:
        trabajador = Trabajador.objects.get(usuario=request.user)
        trabajador.latitud = request.data.get('latitud')
        trabajador.longitud = request.data.get('longitud')
        trabajador.save()
        return Response({'mensaje': 'Ubicación actualizada'})
    except Trabajador.DoesNotExist:
        return Response({'error': 'No tienes perfil de trabajador'}, status=404)

# Admin
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_pendientes(request):
    if request.user.rol != 'admin':
        return Response({'error': 'Sin permisos'}, status=403)
    pendientes = Trabajador.objects.filter(estado='pendiente')
    serializer = TrabajadorAdminSerializer(pendientes, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def aprobar_trabajador(request, pk):
    if request.user.rol != 'admin':
        return Response({'error': 'Sin permisos'}, status=403)
    try:
        trabajador = Trabajador.objects.get(pk=pk)
        trabajador.estado = 'aprobado'
        trabajador.fecha_aprobacion = timezone.now()
        trabajador.motivo_rechazo = ''
        trabajador.save()
        return Response({'mensaje': f'{trabajador.usuario.get_full_name()} aprobado'})
    except Trabajador.DoesNotExist:
        return Response({'error': 'No encontrado'}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rechazar_trabajador(request, pk):
    if request.user.rol != 'admin':
        return Response({'error': 'Sin permisos'}, status=403)
    try:
        trabajador = Trabajador.objects.get(pk=pk)
        trabajador.estado = 'rechazado'
        trabajador.motivo_rechazo = request.data.get('motivo', 'Sin motivo especificado')
        trabajador.save()
        return Response({'mensaje': f'{trabajador.usuario.get_full_name()} rechazado'})
    except Trabajador.DoesNotExist:
        return Response({'error': 'No encontrado'}, status=404)

@api_view(['GET'])
@permission_classes([AllowAny])
def detalle_trabajador(request, pk):
    try:
        trabajador = Trabajador.objects.get(pk=pk, estado='aprobado')
        serializer = TrabajadorSerializer(trabajador)
        return Response(serializer.data)
    except Trabajador.DoesNotExist:
        return Response({'error': 'No encontrado'}, status=404)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_listar_trabajadores(request):
    if request.user.rol != 'admin':
        return Response({'error': 'Sin permisos'}, status=403)
    trabajadores = Trabajador.objects.all()
    serializer = TrabajadorAdminSerializer(trabajadores, many=True)
    return Response(serializer.data)