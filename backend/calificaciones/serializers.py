from rest_framework import serializers
from .models import Calificacion, CalificacionCliente
from usuarios.serializers import UsuarioSerializer
from trabajadores.serializers import TrabajadorSerializer

class CalificacionSerializer(serializers.ModelSerializer):
    cliente = UsuarioSerializer(read_only=True)

    class Meta:
        model = Calificacion
        fields = '__all__'

class CalificacionCrearSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calificacion
        fields = ['trabajador', 'solicitud', 'puntuacion', 'comentario']

    def validate_puntuacion(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('La puntuación debe ser entre 1 y 5')
        return value


class CalificacionClienteSerializer(serializers.ModelSerializer):
    trabajador = TrabajadorSerializer(read_only=True)
    cliente = UsuarioSerializer(read_only=True)

    class Meta:
        model = CalificacionCliente
        fields = '__all__'


class CalificacionClienteCrearSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalificacionCliente
        fields = ['cliente', 'solicitud', 'puntuacion', 'comentario']

    def validate_puntuacion(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('La puntuación debe ser entre 1 y 5')
        return value