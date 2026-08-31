import json
import logging
from unittest.mock import patch
from django.test import TestCase, RequestFactory
from django.http import HttpResponse, JsonResponse
from config.middleware import APIMetricsMiddleware
from analizar_metricas import procesar_fuentes, extraer_json_metrica, calcular_percentil


class MetricsMiddlewareTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_middleware_emite_metrica_json_correcta(self):
        def dummy_view(request):
            return JsonResponse({'status': 'ok'}, status=200)

        middleware = APIMetricsMiddleware(dummy_view)
        request = self.factory.get('/api/trabajadores/')

        with patch.object(logging.getLogger('api.metrics'), 'info') as mock_info:
            response = middleware(request)
            self.assertEqual(response.status_code, 200)

            # Verificar que el logger fue llamado
            self.assertTrue(mock_info.called)
            log_line = mock_info.call_args[0][0]
            data = json.loads(log_line)

            self.assertEqual(data['type'], 'api_metric')
            self.assertEqual(data['method'], 'GET')
            self.assertEqual(data['path'], '/api/trabajadores/')
            self.assertEqual(data['status_code'], 200)
            self.assertEqual(data['status_class'], '2xx')
            self.assertGreaterEqual(data['duration_ms'], 0.0)
            self.assertIn('timestamp', data)

    def test_middleware_captura_errores_4xx_y_5xx(self):
        def error_view(request):
            return HttpResponse('Error de validación', status=400)

        middleware = APIMetricsMiddleware(error_view)
        request = self.factory.post('/api/solicitudes/crear/')

        with patch.object(logging.getLogger('api.metrics'), 'info') as mock_info:
            response = middleware(request)
            self.assertEqual(response.status_code, 400)

            log_line = mock_info.call_args[0][0]
            data = json.loads(log_line)

            self.assertEqual(data['status_code'], 400)
            self.assertEqual(data['status_class'], '4xx')
            self.assertEqual(data['method'], 'POST')


class MetricsAnalyzerTests(TestCase):
    def test_extraer_json_metrica(self):
        linea_pura = '{"type": "api_metric", "method": "GET", "path": "/api/test/", "status_code": 200, "duration_ms": 15.5}'
        linea_railway = '2026-08-29T05:10:20.123Z app[web.1]: {"type": "api_metric", "method": "GET", "path": "/api/test/", "status_code": 200, "duration_ms": 15.5}'

        m1 = extraer_json_metrica(linea_pura)
        m2 = extraer_json_metrica(linea_railway)

        self.assertIsNotNone(m1)
        self.assertIsNotNone(m2)
        self.assertEqual(m1['path'], '/api/test/')
        self.assertEqual(m2['path'], '/api/test/')
        self.assertEqual(m1['duration_ms'], 15.5)

    def test_calcular_percentil(self):
        lista = [10.0, 20.0, 30.0, 40.0, 50.0]
        self.assertEqual(calcular_percentil(lista, 50), 30.0)
        self.assertAlmostEqual(calcular_percentil(lista, 95), 48.0, places=1)

    def test_procesar_fuentes_calcula_metricas_y_tasas_de_error(self):
        logs_ejemplo = [
            '{"type": "api_metric", "method": "GET", "path": "/api/trabajadores/", "status_code": 200, "duration_ms": 20.0, "timestamp": "2026-08-29T10:00:00Z"}',
            '{"type": "api_metric", "method": "GET", "path": "/api/trabajadores/", "status_code": 200, "duration_ms": 40.0, "timestamp": "2026-08-29T10:01:00Z"}',
            '{"type": "api_metric", "method": "POST", "path": "/api/solicitudes/crear/", "status_code": 201, "duration_ms": 50.0, "timestamp": "2026-08-29T10:02:00Z"}',
            '{"type": "api_metric", "method": "POST", "path": "/api/solicitudes/crear/", "status_code": 400, "duration_ms": 30.0, "timestamp": "2026-08-29T10:03:00Z"}',
            '{"type": "api_metric", "method": "GET", "path": "/api/error/", "status_code": 500, "duration_ms": 100.0, "timestamp": "2026-08-29T10:04:00Z"}',
        ]

        resultados, resumen = procesar_fuentes(logs_ejemplo)

        self.assertEqual(resumen['total_solicitudes'], 5)
        self.assertEqual(resumen['total_2xx'], 3)
        self.assertEqual(resumen['total_4xx'], 1)
        self.assertEqual(resumen['total_5xx'], 1)
        self.assertEqual(resumen['tasa_error_global_pct'], 40.0)  # 2 errores de 5 = 40%

        # Verificar desglose de GET /api/trabajadores/
        ep_trab = next(r for r in resultados if r['endpoint'] == 'GET /api/trabajadores/')
        self.assertEqual(ep_trab['volumen'], 2)
        self.assertEqual(ep_trab['avg_ms'], 30.0)
        self.assertEqual(ep_trab['tasa_error_pct'], 0.0)

        # Verificar desglose de POST /api/solicitudes/crear/
        ep_sol = next(r for r in resultados if r['endpoint'] == 'POST /api/solicitudes/crear/')
        self.assertEqual(ep_sol['volumen'], 2)
        self.assertEqual(ep_sol['avg_ms'], 40.0)
        self.assertEqual(ep_sol['tasa_error_pct'], 50.0)  # 1 de 2 = 50%
