from rest_framework import serializers
from .models import Trabajador
from usuarios.serializers import UsuarioSerializer

class TrabajadorSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    foto_url = serializers.SerializerMethodField()

    class Meta:
        model = Trabajador
        fields = '__all__'

    def get_foto_url(self, obj):
        if obj.foto:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.foto.url)
            return obj.foto.url
        return None

class TrabajadorRegistroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trabajador
        fields = ['categoria', 'oficio', 'experiencia', 'descripcion']

class TrabajadorAdminSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)

    class Meta:
        model = Trabajador
        fields = '__all__'