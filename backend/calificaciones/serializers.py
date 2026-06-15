from rest_framework import serializers
from .models import Calificacion
from usuarios.serializers import UsuarioSerializer

class CalificacionSerializer(serializers.ModelSerializer):
    cliente = UsuarioSerializer(read_only=True)

    class Meta:
        model = Calificacion
        fields = '__all__'

class CalificacionCrearSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calificacion
        fields = ['trabajador', 'puntuacion', 'comentario']

    def validate_puntuacion(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('La puntuación debe ser entre 1 y 5')
        return value