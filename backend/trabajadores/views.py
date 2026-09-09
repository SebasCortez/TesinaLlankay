from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from math import radians, sin, cos, sqrt, atan2
from drf_spectacular.utils import extend_schema, OpenApiParameter
from config.file_security import validar_y_sanitizar_imagen
from .models import Trabajador
from .serializers import (
    TrabajadorSerializer,
    TrabajadorRegistroSerializer,
    TrabajadorAdminSerializer,
    TrabajadorActualizarSerializer
)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radio de la Tierra en km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))

@extend_schema(
    summary="Registrar perfil de trabajador para el usuario actual",
    request=TrabajadorRegistroSerializer,
    responses={201: dict, 400: dict}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def registrar_trabajador(request):
    if Trabajador.objects.filter(usuario=request.user).exists():
        return Response({'error': 'Ya tienes un perfil de trabajador registrado.'}, status=status.HTTP_400_BAD_REQUEST)
    serializer = TrabajadorRegistroSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(usuario=request.user)
        if request.user.rol != 'admin':
            request.user.rol = 'trabajador'
            request.user.save()
        return Response({'mensaje': 'Solicitud enviada, pendiente de aprobación por el administrador.'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Listar y filtrar técnicos disponibles con geolocalización y filtros avanzados",
    parameters=[
        OpenApiParameter('categoria', str, description="Filtrar por categoría (ej. Electricidad, Gasfitería)"),
        OpenApiParameter('busqueda', str, description="Texto de búsqueda en oficio o nombre"),
        OpenApiParameter('min_calificacion', float, description="Calificación mínima (ej. 4.0, 4.5)"),
        OpenApiParameter('solo_disponibles', bool, description="Filtrar solo técnicos actualmente disponibles"),
        OpenApiParameter('ordenar_por', str, description="Criterio de orden: 'cercania', 'calificacion', 'servicios'"),
        OpenApiParameter('lat', float, description="Latitud del usuario"),
        OpenApiParameter('lon', float, description="Longitud del usuario"),
        OpenApiParameter('radio', float, description="Radio de búsqueda en km (default: 5)"),
    ],
    responses={200: TrabajadorSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def listar_trabajadores(request):
    trabajadores = Trabajador.objects.filter(estado='aprobado').select_related('usuario')
    categoria = request.query_params.get('categoria')
    busqueda = request.query_params.get('busqueda')
    min_calif = request.query_params.get('min_calificacion')
    solo_disponibles = request.query_params.get('solo_disponibles')
    ordenar_por = request.query_params.get('ordenar_por', 'cercania')
    lat_param = request.query_params.get('lat')
    lon_param = request.query_params.get('lon')
    radio = float(request.query_params.get('radio', 5))

    if categoria:
        trabajadores = trabajadores.filter(categoria=categoria)
    if busqueda:
        trabajadores = trabajadores.filter(
            Q(oficio__icontains=busqueda) |
            Q(usuario__first_name__icontains=busqueda) |
            Q(usuario__last_name__icontains=busqueda) |
            Q(usuario__distrito__icontains=busqueda)
        )
    if min_calif:
        try:
            trabajadores = trabajadores.filter(calificacion_promedio__gte=float(min_calif))
        except (ValueError, TypeError):
            pass
    if solo_disponibles in ['true', '1', True]:
        trabajadores = trabajadores.filter(disponible=True)

    # Optimización geográfica: Bounding box pre-filter en base de datos
    if lat_param and lon_param:
        try:
            user_lat = float(lat_param)
            user_lon = float(lon_param)
            delta_deg = radio / 111.0  # ~111 km por grado
            trabajadores = trabajadores.filter(
                latitud__range=(user_lat - delta_deg, user_lat + delta_deg),
                longitud__range=(user_lon - delta_deg, user_lon + delta_deg)
            )
        except (ValueError, TypeError):
            user_lat, user_lon = None, None
    else:
        user_lat, user_lon = None, None

    resultado = []
    for t in trabajadores:
        data = TrabajadorSerializer(t, context={'request': request}).data
        if user_lat is not None and user_lon is not None and t.latitud and t.longitud:
            distancia = haversine(user_lat, user_lon, t.latitud, t.longitud)
            if distancia <= radio:
                data['distancia_km'] = round(distancia, 1)
                resultado.append(data)
        else:
            data['distancia_km'] = None
            resultado.append(data)

    # Ordenamiento
    if ordenar_por == 'calificacion':
        resultado.sort(key=lambda x: (x.get('calificacion_promedio') or 0, x.get('num_calificaciones') or 0), reverse=True)
    elif ordenar_por == 'servicios':
        resultado.sort(key=lambda x: (x.get('num_calificaciones') or 0, x.get('calificacion_promedio') or 0), reverse=True)
    elif user_lat is not None and user_lon is not None:
        resultado.sort(key=lambda x: x['distancia_km'] if x['distancia_km'] is not None else 999)

    return Response(resultado)


@extend_schema(
    summary="Obtener o actualizar perfil de técnico del usuario actual",
    request=TrabajadorActualizarSerializer,
    responses={200: TrabajadorSerializer, 400: dict, 404: dict}
)
@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def mi_perfil_trabajador(request):
    try:
        trabajador = Trabajador.objects.select_related('usuario').get(usuario=request.user)
    except Trabajador.DoesNotExist:
        return Response({'error': 'No tienes perfil de trabajador'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PATCH':
        serializer = TrabajadorActualizarSerializer(trabajador, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'mensaje': 'Perfil técnico actualizado exitosamente.',
                'trabajador': TrabajadorSerializer(trabajador, context={'request': request}).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer = TrabajadorSerializer(trabajador, context={'request': request})
    return Response(serializer.data)

@extend_schema(
    summary="Actualizar coordenadas GPS del trabajador",
    responses={200: dict, 404: dict}
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def actualizar_ubicacion(request):
    try:
        trabajador = Trabajador.objects.get(usuario=request.user)
        trabajador.latitud = request.data.get('latitud')
        trabajador.longitud = request.data.get('longitud')
        trabajador.save()
        return Response({'mensaje': 'Ubicación actualizada correctamente'})
    except Trabajador.DoesNotExist:
        return Response({'error': 'No tienes perfil de trabajador'}, status=status.HTTP_404_NOT_FOUND)

# Admin
@extend_schema(
    summary="[Admin] Listar técnicos pendientes de aprobación",
    responses={200: TrabajadorAdminSerializer(many=True), 403: dict}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_pendientes(request):
    if request.user.rol != 'admin':
        return Response({'error': 'Sin permisos'}, status=status.HTTP_403_FORBIDDEN)
    pendientes = Trabajador.objects.filter(estado='pendiente').select_related('usuario')
    serializer = TrabajadorAdminSerializer(pendientes, many=True)
    return Response(serializer.data)

@extend_schema(
    summary="[Admin] Aprobar registro de un técnico",
    responses={200: dict, 403: dict, 404: dict}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def aprobar_trabajador(request, pk):
    if request.user.rol != 'admin':
        return Response({'error': 'Sin permisos'}, status=status.HTTP_403_FORBIDDEN)
    try:
        trabajador = Trabajador.objects.get(pk=pk)
        trabajador.estado = 'aprobado'
        trabajador.fecha_aprobacion = timezone.now()
        trabajador.motivo_rechazo = ''
        trabajador.save()
        return Response({'mensaje': f'{trabajador.usuario.get_full_name()} aprobado exitosamente'})
    except Trabajador.DoesNotExist:
        return Response({'error': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)

@extend_schema(
    summary="[Admin] Rechazar registro de un técnico",
    responses={200: dict, 403: dict, 404: dict}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rechazar_trabajador(request, pk):
    if request.user.rol != 'admin':
        return Response({'error': 'Sin permisos'}, status=status.HTTP_403_FORBIDDEN)
    try:
        trabajador = Trabajador.objects.get(pk=pk)
        trabajador.estado = 'rechazado'
        trabajador.motivo_rechazo = request.data.get('motivo', 'Sin motivo especificado')
        trabajador.save()
        return Response({'mensaje': f'{trabajador.usuario.get_full_name()} rechazado'})
    except Trabajador.DoesNotExist:
        return Response({'error': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)

@extend_schema(
    summary="Detalle público de un técnico aprobado",
    responses={200: TrabajadorSerializer, 404: dict}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def detalle_trabajador(request, pk):
    try:
        trabajador = Trabajador.objects.select_related('usuario').get(pk=pk, estado='aprobado')
        serializer = TrabajadorSerializer(trabajador, context={'request': request})
        return Response(serializer.data)
    except Trabajador.DoesNotExist:
        return Response({'error': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)

@extend_schema(
    summary="[Admin] Listar todos los trabajadores registrados",
    responses={200: TrabajadorAdminSerializer(many=True), 403: dict}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_listar_trabajadores(request):
    if request.user.rol != 'admin':
        return Response({'error': 'Sin permisos'}, status=status.HTTP_403_FORBIDDEN)
    trabajadores = Trabajador.objects.all().select_related('usuario')
    serializer = TrabajadorAdminSerializer(trabajadores, many=True)
    return Response(serializer.data)

@extend_schema(
    summary="Alternar disponibilidad (disponible / no disponible)",
    responses={200: dict, 404: dict}
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def toggle_disponibilidad(request):
    try:
        trabajador = Trabajador.objects.get(usuario=request.user)
        trabajador.disponible = not trabajador.disponible
        trabajador.save()
        estado = 'disponible' if trabajador.disponible else 'no disponible'
        return Response({'mensaje': f'Ahora estás {estado}', 'disponible': trabajador.disponible})
    except Trabajador.DoesNotExist:
        return Response({'error': 'No tienes perfil de trabajador'}, status=status.HTTP_404_NOT_FOUND)

@extend_schema(
    summary="Actualizar foto de perfil de trabajador",
    responses={200: dict, 400: dict, 404: dict}
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def actualizar_foto(request):
    try:
        trabajador = Trabajador.objects.get(usuario=request.user)
        if 'foto' not in request.FILES:
            return Response({'error': 'No se envió ninguna foto'}, status=status.HTTP_400_BAD_REQUEST)
        
        foto_raw = request.FILES['foto']
        valido, foto_sanitizada, error_msg = validar_y_sanitizar_imagen(foto_raw, formato_salida='WEBP')
        if not valido or foto_sanitizada is None:
            return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)

        trabajador.foto = foto_sanitizada
        trabajador.save()
        
        # Sincronizar en el usuario también
        request.user.foto = trabajador.foto
        request.user.save()

        return Response({'mensaje': 'Foto actualizada', 'foto': request.build_absolute_uri(trabajador.foto.url)})
    except Trabajador.DoesNotExist:
        return Response({'error': 'No tienes perfil de trabajador'}, status=status.HTTP_404_NOT_FOUND)

from django.core.management import call_command

@extend_schema(
    summary="Poblar datos de técnicos y reseñas para demostración",
    responses={200: dict, 403: dict, 500: dict}
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def poblar_datos_demo(request):
    secret = request.query_params.get('secret') or (request.data.get('secret') if hasattr(request, 'data') else None)
    es_admin = request.user and request.user.is_authenticated and getattr(request.user, 'rol', None) == 'admin'

    if not es_admin and secret != 'llankay2026demo':
        return Response(
            {'error': 'No autorizado. Inicia sesión como administrador o usa el parámetro ?secret=llankay2026demo'},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        call_command('poblar_datos')
        total = Trabajador.objects.filter(estado='aprobado').count()
        return Response({
            'mensaje': f'Base de datos poblada exitosamente. Actualmente hay {total} técnicos cusqueños aprobados en el sistema.',
            'total_trabajadores': total
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': f'Error al poblar datos: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)