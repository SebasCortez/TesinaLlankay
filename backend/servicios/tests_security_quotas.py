import time
from unittest.mock import MagicMock, patch
from django.test import TestCase, override_settings
from django.core.cache import cache
from usuarios.models import Usuario
from usuarios.captcha import generar_captcha_reto, validar_captcha
from config.quotas import verificar_y_consumir_cuota
from servicios.cost_controls import (
    optimizar_historial_turnos,
    verificar_presupuesto_diario_tokens,
    registrar_consumo_tokens
)


class SecurityAndQuotasTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = Usuario.objects.create_user(
            username='test_cliente',
            email='test_cliente@llankay.pe',
            password='Password123!',
            rol='cliente',
            celular='987654321',
            distrito='Wanchaq'
        )

    def tearDown(self):
        cache.clear()

    # 1. CAPTCHA Tests
    def test_generar_y_validar_captcha_exitoso(self):
        reto = generar_captcha_reto()
        self.assertIn("captcha_key", reto)
        self.assertIn("<svg", reto["svg_image"])

        # Intentar validar con respuesta incorrecta
        es_valido, error = validar_captcha(reto["captcha_key"], "999999")
        self.assertFalse(es_valido)
        self.assertIn("incorrecta", error)

    def test_login_requiere_y_valida_captcha(self):
        # Intento de login sin captcha
        res_sin_captcha = self.client.post(
            '/api/usuarios/login/',
            {"username": "test_cliente", "password": "Password123!"},
            content_type='application/json'
        )
        self.assertEqual(res_sin_captcha.status_code, 400)
        self.assertIn("captcha_key", res_sin_captcha.data)

        # Intento de login con captcha inválido
        res_captcha_malo = self.client.post(
            '/api/usuarios/login/',
            {
                "username": "test_cliente",
                "password": "Password123!",
                "captcha_key": "dummy_bad_key",
                "captcha_value": "123"
            },
            content_type='application/json'
        )
        self.assertEqual(res_captcha_malo.status_code, 400)
        self.assertIn("captcha", res_captcha_malo.data)

    # 2. Quotas Tests
    def test_usage_quotas_increment_and_exhaustion(self):
        mock_request = MagicMock()
        mock_request.user = self.user
        mock_request.META = {'REMOTE_ADDR': '127.0.0.1'}

        with override_settings(GROQ_DAILY_USER_QUOTA=3):
            # Consumo 1
            ok1, info1 = verificar_y_consumir_cuota(mock_request, tipo="test_chat", incrementar=True)
            self.assertTrue(ok1)
            self.assertEqual(info1["restantes"], 2)

            # Consumo 2
            ok2, info2 = verificar_y_consumir_cuota(mock_request, tipo="test_chat", incrementar=True)
            self.assertTrue(ok2)
            self.assertEqual(info2["restantes"], 1)

            # Consumo 3
            ok3, info3 = verificar_y_consumir_cuota(mock_request, tipo="test_chat", incrementar=True)
            self.assertTrue(ok3)
            self.assertEqual(info3["restantes"], 0)

            # Consumo 4 (Excedido)
            ok4, info4 = verificar_y_consumir_cuota(mock_request, tipo="test_chat", incrementar=True)
            self.assertFalse(ok4)
            self.assertIn("Has alcanzado tu cuota diaria", info4["mensaje"])

    # 3. Cost Controls Tests
    def test_cost_controls_context_window_truncation(self):
        historial_largo = [{"role": "user", "content": f"Mensaje {i}"} for i in range(25)]
        optimizado = optimizar_historial_turnos(historial_largo, max_turnos=8)
        self.assertEqual(len(optimizado), 8)
        self.assertEqual(optimizado[-1]["content"], "Mensaje 24")

    def test_cost_controls_daily_token_budget(self):
        with override_settings(GROQ_DAILY_GLOBAL_TOKEN_BUDGET=1000):
            # Registrar consumo inicial
            total = registrar_consumo_tokens(600)
            self.assertEqual(total, 600)

            dentro_presupuesto, consumo, max_presupuesto = verificar_presupuesto_diario_tokens()
            self.assertTrue(dentro_presupuesto)

            # Registrar consumo que exceda
            registrar_consumo_tokens(500)
            dentro_presupuesto, consumo, max_presupuesto = verificar_presupuesto_diario_tokens()
            self.assertFalse(dentro_presupuesto)
            self.assertEqual(consumo, 1100)

    # 4. Agente Endpoint con Quotas y Cost Control
    @patch('servicios.views.generar_respuesta_agente')
    def test_agente_endpoint_bloquea_por_cuota_excedida(self, mock_generar):
        mock_generar.return_value = {
            "exito": True,
            "respuesta": "Hola!",
            "error": None,
            "tipo_error": None,
            "uso": {"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20},
            "modelo": "llama-3.3-70b-versatile"
        }

        with override_settings(GROQ_DAILY_IP_QUOTA=2):
            # Request 1: OK
            res1 = self.client.post('/api/agente/chat/', {"mensaje": "Pregunta 1", "historial": []}, content_type='application/json')
            self.assertEqual(res1.status_code, 200)
            self.assertEqual(res1.data["cuota"]["restantes"], 1)

            # Request 2: OK
            res2 = self.client.post('/api/agente/chat/', {"mensaje": "Pregunta 2", "historial": []}, content_type='application/json')
            self.assertEqual(res2.status_code, 200)
            self.assertEqual(res2.data["cuota"]["restantes"], 0)

            # Request 3: HTTP 429 Cuota agotada
            res3 = self.client.post('/api/agente/chat/', {"mensaje": "Pregunta 3", "historial": []}, content_type='application/json')
            self.assertEqual(res3.status_code, 429)
            self.assertFalse(res3.data["exito"])
            self.assertEqual(res3.data["tipo_error"], "quota_exceeded")
            self.assertIn("Retry-After", res3.headers)
