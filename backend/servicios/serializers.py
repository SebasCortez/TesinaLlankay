from rest_framework import serializers


class MensajeTurnoSerializer(serializers.Serializer):
    role = serializers.ChoiceField(
        choices=['user', 'assistant', 'system'],
        help_text="Rol del emisor del mensaje ('user', 'assistant' o 'system')."
    )
    content = serializers.CharField(
        help_text="Contenido del mensaje."
    )


class ChatAgenteRequestSerializer(serializers.Serializer):
    historial = serializers.ListField(
        child=MensajeTurnoSerializer(),
        allow_empty=True,
        required=False,
        default=list,
        help_text="Historial de mensajes previos de la conversación."
    )
    mensaje = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Último mensaje del usuario (si no se incluye dentro de historial)."
    )
    system_prompt = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Prompt de sistema personalizado (opcional)."
    )
    modelo = serializers.CharField(
        required=False,
        default='llama-3.3-70b-versatile',
        help_text="Modelo Groq a utilizar (default: 'llama-3.3-70b-versatile')."
    )
    temperatura = serializers.FloatField(
        required=False,
        default=0.7,
        min_value=0.0,
        max_value=2.0,
        help_text="Temperatura para la generación."
    )
    max_tokens = serializers.IntegerField(
        required=False,
        default=1024,
        min_value=1,
        max_value=8192,
        help_text="Máximo número de tokens a generar."
    )


class UsoTokensSerializer(serializers.Serializer):
    prompt_tokens = serializers.IntegerField(required=False)
    completion_tokens = serializers.IntegerField(required=False)
    total_tokens = serializers.IntegerField(required=False)


class CuotaUsoSerializer(serializers.Serializer):
    restantes = serializers.IntegerField(required=False)
    limite_diario = serializers.IntegerField(required=False)
    segundos_reinicio = serializers.IntegerField(required=False)


class ChatAgenteResponseSerializer(serializers.Serializer):
    exito = serializers.BooleanField()
    respuesta = serializers.CharField(allow_null=True)
    error = serializers.CharField(allow_null=True, required=False)
    tipo_error = serializers.CharField(allow_null=True, required=False)
    uso = UsoTokensSerializer(allow_null=True, required=False)
    cuota = CuotaUsoSerializer(allow_null=True, required=False)
    modelo = serializers.CharField()

