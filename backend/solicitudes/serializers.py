from rest_framework import serializers
from .models import Solicitud
from usuarios.serializers import UsuarioSerializer
from trabajadores.serializers import TrabajadorSerializer

class SolicitudSerializer(serializers.ModelSerializer):
    cliente = UsuarioSerializer(read_only=True)
    trabajador = TrabajadorSerializer(read_only=True)
    ha_calificado_trabajador = serializers.SerializerMethodField()
    ha_calificado_cliente = serializers.SerializerMethodField()

    class Meta:
        model = Solicitud
        fields = '__all__'

    def get_ha_calificado_trabajador(self, obj):
        from calificaciones.models import Calificacion
        return Calificacion.objects.filter(solicitud=obj).exists()

    def get_ha_calificado_cliente(self, obj):
        from calificaciones.models import CalificacionCliente
        return CalificacionCliente.objects.filter(solicitud=obj).exists()

class SolicitudCrearSerializer(serializers.ModelSerializer):
    mensaje = serializers.CharField(min_length=5, max_length=300, trim_whitespace=True)
    descripcion_problema = serializers.CharField(min_length=10, max_length=1500, trim_whitespace=True)
    direccion = serializers.CharField(min_length=5, max_length=200, trim_whitespace=True)

    class Meta:
        model = Solicitud
        fields = ['trabajador', 'mensaje', 'descripcion_problema', 'direccion']

from .models import RequerimientoOficio

class RequerimientoOficioSerializer(serializers.ModelSerializer):
    cliente = UsuarioSerializer(read_only=True)

    class Meta:
        model = RequerimientoOficio
        fields = '__all__'

class RequerimientoOficioCrearSerializer(serializers.ModelSerializer):
    nombre_contacto = serializers.CharField(min_length=2, max_length=100, trim_whitespace=True)
    celular_contacto = serializers.CharField(min_length=9, max_length=15, trim_whitespace=True)
    distrito = serializers.CharField(max_length=100, default='Wanchaq')
    oficio_solicitado = serializers.CharField(min_length=3, max_length=150, trim_whitespace=True)
    descripcion = serializers.CharField(max_length=800, required=False, allow_blank=True, trim_whitespace=True)

    class Meta:
        model = RequerimientoOficio
        fields = ['nombre_contacto', 'celular_contacto', 'distrito', 'oficio_solicitado', 'descripcion']