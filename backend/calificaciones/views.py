from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Calificacion
from .serializers import CalificacionSerializer, CalificacionCrearSerializer
from trabajadores.models import Trabajador

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_calificacion(request):
    if request.user.rol != 'cliente':
        return Response({'error': 'Solo clientes pueden calificar'}, status=403)

    serializer = CalificacionCrearSerializer(data=request.data)
    if serializer.is_valid():
        trabajador_id = serializer.validated_data['trabajador'].id

        if Calificacion.objects.filter(
            trabajador_id=trabajador_id,
            cliente=request.user
        ).exists():
            return Response({'error': 'Ya calificaste a este trabajador'}, status=400)

        calificacion = serializer.save(cliente=request.user)

        # Recalcular promedio
        trabajador = Trabajador.objects.get(pk=trabajador_id)
        calificaciones = Calificacion.objects.filter(trabajador=trabajador)
        trabajador.calificacion_promedio = sum(c.puntuacion for c in calificaciones) / calificaciones.count()
        trabajador.num_calificaciones = calificaciones.count()
        trabajador.save()

        return Response({'mensaje': 'Calificación registrada'}, status=201)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([AllowAny])
def listar_calificaciones(request, trabajador_id):
    calificaciones = Calificacion.objects.filter(
        trabajador_id=trabajador_id
    ).order_by('-fecha')
    serializer = CalificacionSerializer(calificaciones, many=True)
    return Response(serializer.data)