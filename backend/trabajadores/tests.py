from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from usuarios.models import Usuario
from trabajadores.models import Trabajador
from trabajadores.views import haversine

class TrabajadorTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_tecnico = Usuario.objects.create_user(
            username='miguel_gasfitero',
            email='miguel@example.com',
            password='Password123!',
            first_name='Miguel',
            last_name='Quispe',
            rol='trabajador',
            celular='984998877',
            distrito='San Sebastián'
        )
        self.trabajador = Trabajador.objects.create(
            usuario=self.user_tecnico,
            categoria='Gasfitería',
            oficio='Gasfitero especializado en termas y tuberías',
            experiencia='3-5 años',
            descripcion='Servicio rápido y garantizado',
            disponible=True,
            estado='aprobado',
            latitud=-13.5250,
            longitud=-71.9500
        )

    def test_haversine_calculo(self):
        # Distancia entre dos puntos cercanos en Cusco (~1.5 km)
        dist = haversine(-13.5170, -71.9785, -13.5250, -71.9500)
        self.assertGreater(dist, 1.0)
        self.assertLess(dist, 5.0)

    def test_listar_trabajadores_aprobados(self):
        response = self.client.get('/api/trabajadores/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['oficio'], 'Gasfitero especializado en termas y tuberías')

    def test_filtrar_por_categoria(self):
        response = self.client.get('/api/trabajadores/?categoria=Gasfitería')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        response_empty = self.client.get('/api/trabajadores/?categoria=Electricidad')
        self.assertEqual(len(response_empty.data), 0)

    def test_toggle_disponibilidad(self):
        self.client.force_authenticate(user=self.user_tecnico)
        response = self.client.patch('/api/trabajadores/disponibilidad/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['disponible'])

    def test_actualizar_mi_perfil_trabajador(self):
        self.client.force_authenticate(user=self.user_tecnico)
        payload = {
            'oficio': 'Gasfitero y Especialista en Termas Solares',
            'experiencia': 'Más de 5 años',
            'descripcion': 'Atención 24/7 en todo Cusco'
        }
        response = self.client.patch('/api/trabajadores/mi-perfil/', payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.trabajador.refresh_from_db()
        self.assertEqual(self.trabajador.oficio, 'Gasfitero y Especialista en Termas Solares')
        self.assertEqual(self.trabajador.experiencia, 'Más de 5 años')

