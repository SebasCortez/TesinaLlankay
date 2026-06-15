from rest_framework import serializers
from .models import Solicitud
from usuarios.serializers import UsuarioSerializer
from trabajadores.serializers import TrabajadorSerializer

class SolicitudSerializer(serializers.ModelSerializer):
    cliente = UsuarioSerializer(read_only=True)
    trabajador = TrabajadorSerializer(read_only=True)

    class Meta:
        model = Solicitud
        fields = '__all__'

class SolicitudCrearSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solicitud
        fields = ['trabajador', 'mensaje', 'descripcion_problema', 'direccion']