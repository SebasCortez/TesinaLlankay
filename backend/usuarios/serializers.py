from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Usuario

class RegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'password', 'rol', 'celular', 'distrito']

    def validate_celular(self, value):
        if value:
            clean_val = value.strip().replace(' ', '').replace('-', '')
            if len(clean_val) != 9 or not clean_val.isdigit():
                raise serializers.ValidationError('El celular debe tener 9 dígitos numéricos.')
            return clean_val
        return value

    def create(self, validated_data):
        user = Usuario.objects.create_user(**validated_data)
        return user


class UsuarioSerializer(serializers.ModelSerializer):
    foto_url = serializers.SerializerMethodField()
    reputacion_promedio = serializers.SerializerMethodField()
    num_calificaciones = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'rol', 'celular', 'distrito', 'foto', 'foto_url', 'fecha_registro',
                  'reputacion_promedio', 'num_calificaciones']

    def get_foto_url(self, obj):
        if obj.foto:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.foto.url)
            return obj.foto.url
        return None

    def get_reputacion_promedio(self, obj):
        from django.db.models import Avg
        from calificaciones.models import CalificacionCliente
        if CalificacionCliente.objects.filter(cliente=obj).exists():
            agg = CalificacionCliente.objects.filter(cliente=obj).aggregate(promedio=Avg('puntuacion'))
            return round(agg['promedio'] or 0.0, 1)
        return None

    def get_num_calificaciones(self, obj):
        from calificaciones.models import CalificacionCliente
        return CalificacionCliente.objects.filter(cliente=obj).count()


class ActualizarUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'celular', 'distrito']

    def validate_celular(self, value):
        if value:
            clean_val = value.strip().replace(' ', '').replace('-', '')
            if len(clean_val) != 9 or not clean_val.isdigit():
                raise serializers.ValidationError('El celular debe tener 9 dígitos numéricos.')
            return clean_val
        return value

    def validate_email(self, value):
        if value:
            clean_email = value.strip().lower()
            user = self.instance
            if Usuario.objects.filter(email__iexact=clean_email).exclude(pk=user.pk if user else None).exists():
                raise serializers.ValidationError('Este correo electrónico ya está registrado por otro usuario.')
            return clean_email
        return value


class CambiarPasswordSerializer(serializers.Serializer):
    password_actual = serializers.CharField(write_only=True)
    password_nueva = serializers.CharField(write_only=True, min_length=8)

    def validate_password_nueva(self, value):
        if len(value) < 8:
            raise serializers.ValidationError('La nueva contraseña debe tener al menos 8 caracteres.')
        return value


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    captcha_key = serializers.CharField(required=True, write_only=True, help_text="Token firmado del CAPTCHA")
    captcha_value = serializers.CharField(required=True, write_only=True, help_text="Respuesta ingresada por el usuario al reto CAPTCHA")

    def validate(self, data):
        from .captcha import validar_captcha
        from django.contrib.auth import authenticate

        captcha_key = data.pop('captcha_key', '')
        captcha_value = data.pop('captcha_value', '')

        # 1. Validar reto CAPTCHA
        es_valido, error_captcha = validar_captcha(captcha_key, captcha_value)
        if not es_valido:
            raise serializers.ValidationError({'captcha': error_captcha})

        # 2. Autenticar credenciales
        user = authenticate(**data)
        if not user:
            raise serializers.ValidationError('Credenciales incorrectas')
        tokens = RefreshToken.for_user(user)
        return {
            'access': str(tokens.access_token),
            'refresh': str(tokens),
            'usuario': UsuarioSerializer(user).data
        }


class RecuperarPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class RestablecerPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=8)


class GoogleAuthSerializer(serializers.Serializer):
    credential = serializers.CharField(help_text="Google ID Token recibido desde Google Identity Services")