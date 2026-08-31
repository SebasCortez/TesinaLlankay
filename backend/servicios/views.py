from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiExample
from config.throttling import AgenteChatRateThrottle
from config.quotas import verificar_y_consumir_cuota
from .cost_controls import (
    optimizar_historial_turnos,
    verificar_presupuesto_diario_tokens,
    registrar_consumo_tokens,
    MAX_TOKENS_CEILING
)
from .groq_agent import generar_respuesta_agente, GROQ_DEFAULT_MODEL
from .serializers import ChatAgenteRequestSerializer, ChatAgenteResponseSerializer

PROMPT_SISTEMA_DEFAULT = (
    "Eres LlankAI, el asistente virtual inteligente de Llankay (Plataforma de Servicios Técnicos en Cusco, Perú). "
    "Tu función principal es orientar y ayudar a los usuarios a encontrar el técnico o servicio adecuado "
    "(electricidad, gasfitería/plomería, cerrajería, carpintería, albañilería, etc.). "
    "Responde siempre de forma amable, empática, profesional y concisa. Si te preguntan por ubicación, recuerda "
    "que el servicio opera en los distritos de Cusco (Cusco Centro, Wanchaq, San Sebastián, San Jerónimo, Santiago, etc.)."
)


class AgenteChatAPIView(APIView):
    """
    Endpoint para interactuar con el agente conversacional inteligente LlankAI impulsado por Groq y LLaMA 3.3 70B.
    Protegido con Rate Limiting (15/min), Cuotas de Uso Diarias y Control de Presupuesto de Tokens.
    """
    permission_classes = [AllowAny]
    throttle_classes = [AgenteChatRateThrottle]

    @extend_schema(
        summary="Conversar con el agente de IA LlankAI (Groq - LLaMA 3.3 70B)",
        description="Envía un historial de conversación o un nuevo mensaje al agente conversacional LlankAI de Llankay. "
                    "Incluye control de cuotas diarias, rate limiting y optimización de tokens.",
        request=ChatAgenteRequestSerializer,
        responses={
            200: ChatAgenteResponseSerializer,
            429: ChatAgenteResponseSerializer,
            500: ChatAgenteResponseSerializer,
            503: ChatAgenteResponseSerializer,
        },
        examples=[
            OpenApiExample(
                "Ejemplo de consulta",
                value={
                    "mensaje": "Hola, necesito un gasfitero urgente en Wanchaq porque tengo una fuga de agua.",
                    "historial": []
                },
                request_only=True,
            )
        ]
    )
    def post(self, request):
        # 1. Verificar Cuota Diaria del Usuario / IP
        cuota_ok, info_cuota = verificar_y_consumir_cuota(request, tipo="agente_chat", incrementar=True)
        if not cuota_ok:
            return Response({
                "exito": False,
                "respuesta": None,
                "error": info_cuota["mensaje"],
                "tipo_error": "quota_exceeded",
                "uso": None,
                "cuota": {
                    "restantes": 0,
                    "limite_diario": info_cuota["limite_diario"],
                    "segundos_reinicio": info_cuota["segundos_reinicio"]
                },
                "modelo": GROQ_DEFAULT_MODEL
            }, status=status.HTTP_429_TOO_MANY_REQUESTS, headers={"Retry-After": str(info_cuota["segundos_reinicio"])})

        # 2. Verificar Presupuesto Global de Tokens (Cost Controls)
        presupuesto_ok, consumo_actual, presupuesto_max = verificar_presupuesto_diario_tokens()
        if not presupuesto_ok:
            return Response({
                "exito": False,
                "respuesta": None,
                "error": "El servicio de IA ha alcanzado su límite de presupuesto diario global. Por favor intenta mañana.",
                "tipo_error": "cost_limit_reached",
                "uso": None,
                "cuota": {
                    "restantes": info_cuota["restantes"],
                    "limite_diario": info_cuota["limite_diario"],
                    "segundos_reinicio": info_cuota["segundos_reinicio"]
                },
                "modelo": GROQ_DEFAULT_MODEL
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 3. Validar payload de entrada
        serializer = ChatAgenteRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        datos = serializer.validated_data
        historial = list(datos.get('historial', []))
        nuevo_mensaje = datos.get('mensaje')
        system_prompt = datos.get('system_prompt') or PROMPT_SISTEMA_DEFAULT
        modelo = datos.get('modelo') or GROQ_DEFAULT_MODEL
        temperatura = datos.get('temperatura', 0.7)
        max_tokens = min(datos.get('max_tokens', 1024), MAX_TOKENS_CEILING)

        if nuevo_mensaje:
            historial.append({'role': 'user', 'content': nuevo_mensaje})

        # 4. Optimizar ventana de contexto (Cost Controls)
        historial_optimizado = optimizar_historial_turnos(historial)

        # 5. Generar respuesta con Groq
        resultado = generar_respuesta_agente(
            system_prompt=system_prompt,
            historial=historial_optimizado,
            modelo=modelo,
            temperatura=temperatura,
            max_tokens=max_tokens
        )

        # 6. Registrar consumo de tokens si fue exitoso
        if resultado.get("exito") and resultado.get("uso"):
            registrar_consumo_tokens(resultado["uso"]["total_tokens"])

        # Adjuntar metadata de cuota restante
        resultado["cuota"] = {
            "restantes": info_cuota["restantes"],
            "limite_diario": info_cuota["limite_diario"],
            "segundos_reinicio": info_cuota["segundos_reinicio"]
        }

        response_serializer = ChatAgenteResponseSerializer(resultado)

        if not resultado["exito"]:
            tipo = resultado.get("tipo_error")
            if tipo == "rate_limit":
                http_status = status.HTTP_429_TOO_MANY_REQUESTS
            elif tipo == "timeout":
                http_status = status.HTTP_504_GATEWAY_TIMEOUT
            elif tipo == "auth":
                http_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            elif tipo == "connection":
                http_status = status.HTTP_503_SERVICE_UNAVAILABLE
            else:
                http_status = status.HTTP_500_INTERNAL_SERVER_ERROR

            return Response(response_serializer.data, status=http_status)

        return Response(response_serializer.data, status=status.HTTP_200_OK)

