from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from usuarios.models import Usuario
from trabajadores.models import Trabajador
from solicitudes.models import Solicitud
from calificaciones.models import Calificacion, CalificacionCliente


class CalificacionesBidireccionalesTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # 1. Crear Cliente
        self.cliente = Usuario.objects.create_user(
            username='carlos_cliente',
            email='carlos@llankay.pe',
            password='Password123!',
            first_name='Carlos',
            last_name='Mendoza',
            rol='cliente',
            celular='987654321',
            distrito='Wanchaq'
        )

        # 2. Crear Técnico
        self.user_tecnico = Usuario.objects.create_user(
            username='juan_tecnico',
            email='juan@llankay.pe',
            password='Password123!',
            first_name='Juan',
            last_name='Quispe',
            rol='trabajador',
            celular='912345678',
            distrito='San Sebastián'
        )
        self.trabajador = Trabajador.objects.create(
            usuario=self.user_tecnico,
            categoria='Electricidad',
            oficio='Técnico Electricista',
            experiencia='3-5 años',
            descripcion='Instalaciones domiciliarias en Cusco',
            estado='aprobado',
            disponible=True
        )

        # 3. Crear Otro Usuario
        self.otro_usuario = Usuario.objects.create_user(
            username='pedro_cliente',
            email='pedro@llankay.pe',
            password='Password123!',
            first_name='Pedro',
            last_name='Gomez',
            rol='cliente',
            celular='923456789',
            distrito='Cusco'
        )

        # 4. Crear Solicitud Completada
        self.solicitud_completada = Solicitud.objects.create(
            cliente=self.cliente,
            trabajador=self.trabajador,
            mensaje='Reparación de cortocircuito',
            descripcion_problema='Se cayó la llave térmica principal.',
            direccion='Av. Garcilaso 450, Wanchaq',
            estado='completado',
            precio_acordado=80.00,
            metodo_pago='Yape'
        )

        # 5. Crear Solicitud Pendiente
        self.solicitud_pendiente = Solicitud.objects.create(
            cliente=self.otro_usuario,
            trabajador=self.trabajador,
            mensaje='Cambio de tomacorrientes',
            descripcion_problema='Instalar 4 tomacorrientes dobles.',
            direccion='Calle Saphy 123, Cusco',
            estado='pendiente'
        )

    # 1. Calificación Cliente → Técnico
    def test_cliente_califica_trabajador_exitoso(self):
        self.client.force_authenticate(user=self.cliente)
        payload = {
            'trabajador': self.trabajador.id,
            'solicitud': self.solicitud_completada.id,
            'puntuacion': 5,
            'comentario': 'Excelente servicio, muy puntual y ordenado.'
        }
        res = self.client.post('/api/calificaciones/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Calificacion.objects.filter(solicitud=self.solicitud_completada).exists())

        self.trabajador.refresh_from_db()
        self.assertEqual(self.trabajador.calificacion_promedio, 5.0)
        self.assertEqual(self.trabajador.num_calificaciones, 1)

    # 2. Calificación Técnico → Cliente (Viceversa)
    def test_tecnico_califica_cliente_exitoso(self):
        self.client.force_authenticate(user=self.user_tecnico)
        payload = {
            'cliente': self.cliente.id,
            'solicitud': self.solicitud_completada.id,
            'puntuacion': 5,
            'comentario': 'Cliente muy amable y pago puntual por Yape.'
        }
        res = self.client.post('/api/calificaciones/cliente/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CalificacionCliente.objects.filter(solicitud=self.solicitud_completada).exists())

        # Verificar reputación del cliente en perfil
        res_perfil = self.client.get(f'/api/calificaciones/cliente/{self.cliente.id}/')
        self.assertEqual(res_perfil.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_perfil.data), 1)
        self.assertEqual(res_perfil.data[0]['puntuacion'], 5)

    # 3. Técnico no puede calificar una solicitud que no esté completada
    def test_tecnico_no_puede_calificar_solicitud_pendiente(self):
        self.client.force_authenticate(user=self.user_tecnico)
        payload = {
            'cliente': self.otro_usuario.id,
            'solicitud': self.solicitud_pendiente.id,
            'puntuacion': 4,
            'comentario': 'Aún en proceso.'
        }
        res = self.client.post('/api/calificaciones/cliente/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('completadas', res.data.get('error', ''))

    # 4. No se permiten calificaciones duplicadas para la misma solicitud
    def test_bloqueo_calificaciones_duplicadas_cliente(self):
        self.client.force_authenticate(user=self.user_tecnico)
        payload = {
            'cliente': self.cliente.id,
            'solicitud': self.solicitud_completada.id,
            'puntuacion': 5,
            'comentario': 'Primera calificación.'
        }
        res1 = self.client.post('/api/calificaciones/cliente/', payload, format='json')
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)

        # Intento de duplicado
        res2 = self.client.post('/api/calificaciones/cliente/', payload, format='json')
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Ya has calificado', res2.data.get('error', ''))

    # 5. Usuario sin perfil de trabajador no puede calificar clientes
    def test_usuario_regular_no_puede_calificar_clientes(self):
        self.client.force_authenticate(user=self.otro_usuario)
        payload = {
            'cliente': self.cliente.id,
            'solicitud': self.solicitud_completada.id,
            'puntuacion': 4,
            'comentario': 'Intento no autorizado'
        }
        res = self.client.post('/api/calificaciones/cliente/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
