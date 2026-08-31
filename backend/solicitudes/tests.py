from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from usuarios.models import Usuario
from trabajadores.models import Trabajador
from solicitudes.models import Solicitud

class SolicitudesAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Usuario 1: Técnico Electricista
        self.tecnico1_user = Usuario.objects.create_user(
            username='carlos_electrico',
            email='carlos.elec@example.com',
            password='Password123!',
            first_name='Carlos',
            last_name='Electricista',
            rol='trabajador',
            celular='984111222',
            distrito='Wanchaq'
        )
        self.tecnico1 = Trabajador.objects.create(
            usuario=self.tecnico1_user,
            categoria='Electricidad',
            oficio='Electricista Matriculado',
            experiencia='3-5 años',
            estado='aprobado'
        )

        # Usuario 2: Técnico Gasfitero
        self.tecnico2_user = Usuario.objects.create_user(
            username='miguel_gasfitero',
            email='miguel.gas@example.com',
            password='Password123!',
            first_name='Miguel',
            last_name='Gasfitero',
            rol='trabajador',
            celular='984333444',
            distrito='San Sebastián'
        )
        self.tecnico2 = Trabajador.objects.create(
            usuario=self.tecnico2_user,
            categoria='Gasfitería',
            oficio='Gasfitero de Termas y Fugas',
            experiencia='Más de 5 años',
            estado='aprobado'
        )

    def test_tecnico_puede_solicitar_servicio_a_otro_tecnico(self):
        # Carlos (electricista) contrata a Miguel (gasfitero)
        self.client.force_authenticate(user=self.tecnico1_user)
        payload = {
            'trabajador': self.tecnico2.id,
            'mensaje': 'Hola Miguel, tengo una fuga de agua en mi taller.',
            'descripcion_problema': 'Fuga en el tubo principal de agua caliente.',
            'direccion': 'Av. Huayruropata 450, Wanchaq'
        }
        response = self.client.post('/api/solicitudes/crear/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Solicitud.objects.filter(cliente=self.tecnico1_user, trabajador=self.tecnico2).exists())

    def test_usuario_no_puede_contratarse_a_si_mismo(self):
        # Carlos intenta enviarse solicitud a sí mismo
        self.client.force_authenticate(user=self.tecnico1_user)
        payload = {
            'trabajador': self.tecnico1.id,
            'mensaje': 'Auto-solicitud de prueba',
            'descripcion_problema': 'Problema de prueba para auto-solicitud',
            'direccion': 'Cusco'
        }
        response = self.client.post('/api/solicitudes/crear/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_filtrar_solicitudes_enviadas_vs_recibidas(self):
        # Crear una solicitud de Carlos a Miguel
        solicitud = Solicitud.objects.create(
            cliente=self.tecnico1_user,
            trabajador=self.tecnico2,
            mensaje='Ayuda con gasfitería',
            descripcion_problema='Goteo constante',
            direccion='Wanchaq'
        )

        # 1. Carlos consulta sus solicitudes enviadas
        self.client.force_authenticate(user=self.tecnico1_user)
        res_enviadas = self.client.get('/api/solicitudes/?tipo=enviadas')
        self.assertEqual(res_enviadas.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_enviadas.data), 1)
        self.assertEqual(res_enviadas.data[0]['id'], solicitud.id)

        # Carlos consulta sus recibidas (debe ser 0)
        res_recibidas_carlos = self.client.get('/api/solicitudes/?tipo=recibidas')
        self.assertEqual(res_recibidas_carlos.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_recibidas_carlos.data), 0)

        # 2. Miguel consulta sus solicitudes recibidas (debe ser 1)
        self.client.force_authenticate(user=self.tecnico2_user)
        res_recibidas_miguel = self.client.get('/api/solicitudes/?tipo=recibidas')
        self.assertEqual(res_recibidas_miguel.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_recibidas_miguel.data), 1)

    def test_actualizar_estado_por_tecnico(self):
        solicitud = Solicitud.objects.create(
            cliente=self.tecnico1_user,
            trabajador=self.tecnico2,
            mensaje='Ayuda',
            descripcion_problema='Problema',
            direccion='San Sebastián'
        )
        self.client.force_authenticate(user=self.tecnico2_user)
        response = self.client.patch(f'/api/solicitudes/{solicitud.id}/estado/', {'estado': 'aceptado'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        solicitud.refresh_from_db()
        self.assertEqual(solicitud.estado, 'aceptado')
