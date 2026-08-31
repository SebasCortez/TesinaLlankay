from unittest.mock import MagicMock, patch
from django.test import TestCase
from openai import RateLimitError, APITimeoutError, AuthenticationError
from servicios.groq_agent import obtener_cliente_groq, generar_respuesta_agente, GROQ_BASE_URL


class GroqAgentTests(TestCase):
    def test_obtener_cliente_groq_configuracion(self):
        cliente = obtener_cliente_groq(api_key="test_gsk_key", timeout=15.0)
        self.assertEqual(str(cliente.base_url), f"{GROQ_BASE_URL}/")
        self.assertEqual(cliente.api_key, "test_gsk_key")
        self.assertEqual(cliente.timeout, 15.0)

    def test_generar_respuesta_agente_exitoso(self):
        mock_cliente = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="¡Hola! Soy tu asistente de servicios técnicos en Cusco."))
        ]
        mock_response.usage = MagicMock(prompt_tokens=25, completion_tokens=15, total_tokens=40)
        mock_cliente.chat.completions.create.return_value = mock_response

        system_prompt = "Eres un asistente técnico en Cusco."
        historial = [
            {"role": "user", "content": "¿Tienen electricistas en Wanchaq?"},
            {"role": "assistant", "content": "Sí, contamos con técnicos verificados en Wanchaq."},
            {"role": "user", "content": "¿Cómo solicito uno?"}
        ]

        resultado = generar_respuesta_agente(
            system_prompt=system_prompt,
            historial=historial,
            cliente=mock_cliente
        )

        self.assertTrue(resultado["exito"])
        self.assertEqual(resultado["respuesta"], "¡Hola! Soy tu asistente de servicios técnicos en Cusco.")
        self.assertIsNone(resultado["error"])
        self.assertEqual(resultado["modelo"], "llama-3.3-70b-versatile")
        self.assertEqual(resultado["uso"]["total_tokens"], 40)

        # Verificar que se enviaron los mensajes completos (system + 3 turnos)
        llamada_args = mock_cliente.chat.completions.create.call_args[1]
        mensajes_enviados = llamada_args["messages"]
        self.assertEqual(len(mensajes_enviados), 4)
        self.assertEqual(mensajes_enviados[0]["role"], "system")
        self.assertEqual(mensajes_enviados[0]["content"], system_prompt)
        self.assertEqual(mensajes_enviados[1]["content"], "¿Tienen electricistas en Wanchaq?")

    def test_generar_respuesta_agente_manejo_rate_limit(self):
        mock_cliente = MagicMock()
        mock_cliente.chat.completions.create.side_effect = RateLimitError(
            message="Rate limit reached for model llama-3.3-70b-versatile",
            response=MagicMock(status_code=429),
            body=None
        )

        resultado = generar_respuesta_agente(
            system_prompt="Test",
            historial=[{"role": "user", "content": "Hola"}],
            cliente=mock_cliente,
            max_reintentos_rate_limit=0
        )

        self.assertFalse(resultado["exito"])
        self.assertIsNone(resultado["respuesta"])
        self.assertEqual(resultado["tipo_error"], "rate_limit")
        self.assertIn("límite de solicitudes", resultado["error"])

    def test_generar_respuesta_agente_manejo_timeout(self):
        mock_cliente = MagicMock()
        mock_cliente.chat.completions.create.side_effect = APITimeoutError(request=MagicMock())

        resultado = generar_respuesta_agente(
            system_prompt="Test",
            historial=[{"role": "user", "content": "Hola"}],
            cliente=mock_cliente
        )

        self.assertFalse(resultado["exito"])
        self.assertEqual(resultado["tipo_error"], "timeout")
        self.assertIn("timeout", resultado["error"])

    def test_generar_respuesta_agente_manejo_auth_error(self):
        mock_cliente = MagicMock()
        mock_cliente.chat.completions.create.side_effect = AuthenticationError(
            message="Invalid API Key",
            response=MagicMock(status_code=401),
            body=None
        )

        resultado = generar_respuesta_agente(
            system_prompt="Test",
            historial=[{"role": "user", "content": "Hola"}],
            cliente=mock_cliente
        )

        self.assertFalse(resultado["exito"])
        self.assertEqual(resultado["tipo_error"], "auth")
        self.assertIn("GROQ_API_KEY", resultado["error"])

    @patch('servicios.views.generar_respuesta_agente')
    def test_endpoint_chat_agente_post_exitoso(self, mock_generar):
        mock_generar.return_value = {
            "exito": True,
            "respuesta": "Hola, te puedo recomendar un técnico en Cusco.",
            "error": None,
            "tipo_error": None,
            "uso": {"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20},
            "modelo": "llama-3.3-70b-versatile"
        }

        response = self.client.post(
            '/api/agente/chat/',
            {
                "mensaje": "¿Qué servicios ofrecen?",
                "historial": []
            },
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["exito"])
        self.assertEqual(response.data["respuesta"], "Hola, te puedo recomendar un técnico en Cusco.")

    @patch('servicios.views.generar_respuesta_agente')
    def test_endpoint_chat_agente_rate_limit(self, mock_generar):
        mock_generar.return_value = {
            "exito": False,
            "respuesta": None,
            "error": "Límite de peticiones alcanzado.",
            "tipo_error": "rate_limit",
            "uso": None,
            "modelo": "llama-3.3-70b-versatile"
        }

        response = self.client.post(
            '/api/agente/chat/',
            {
                "mensaje": "¿Hay disponibilidad?",
                "historial": []
            },
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 429)
        self.assertFalse(response.data["exito"])
        self.assertEqual(response.data["tipo_error"], "rate_limit")

