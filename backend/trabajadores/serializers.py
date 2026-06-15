from rest_framework import serializers
from .models import Trabajador
from usuarios.serializers import UsuarioSerializer

class TrabajadorSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)

    class Meta:
        model = Trabajador
        fields = '__all__'

class TrabajadorRegistroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trabajador
        fields = ['categoria', 'oficio', 'experiencia', 'descripcion']

class TrabajadorAdminSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)

    class Meta:
        model = Trabajador
        fields = '__all__'