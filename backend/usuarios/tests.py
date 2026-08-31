import io
from PIL import Image
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework.test import APIClient
from rest_framework import status
from usuarios.models import Usuario
from usuarios.captcha import generar_captcha_para_test

class UsuarioAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.cliente_user = Usuario.objects.create_user(
            username='carlos_cliente',
            email='carlos@example.com',
            password='Password123!',
            first_name='Carlos',
            last_name='Huanca',
            rol='cliente',
            celular='984112233',
            distrito='Wanchaq'
        )

    def test_registro_usuario_exitoso(self):
        payload = {
            'username': 'nuevo_usuario',
            'email': 'nuevo@example.com',
            'password': 'PasswordSeguro123!',
            'first_name': 'Juan',
            'last_name': 'Perez',
            'rol': 'cliente',
            'celular': '984112233',
            'distrito': 'Cusco'
        }
        response = self.client.post('/api/usuarios/registro/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Usuario.objects.filter(username='nuevo_usuario').exists())

    def test_registro_celular_invalido(self):
        payload = {
            'username': 'usuario_malo',
            'email': 'malo@example.com',
            'password': 'PasswordSeguro123!',
            'first_name': 'Juan',
            'last_name': 'Perez',
            'rol': 'cliente',
            'celular': '1234',  # Menos de 9 dígitos
            'distrito': 'Cusco'
        }
        response = self.client.post('/api/usuarios/registro/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_exitoso_y_obtener_tokens(self):
        captcha_key, captcha_val = generar_captcha_para_test()
        payload = {
            'username': 'carlos_cliente',
            'password': 'Password123!',
            'captcha_key': captcha_key,
            'captcha_value': captcha_val
        }
        response = self.client.post('/api/usuarios/login/', payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['usuario']['username'], 'carlos_cliente')

    def test_recuperar_password_solicitud(self):
        payload = {'email': 'carlos@example.com'}
        response = self.client.post('/api/usuarios/recuperar-password/', payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('mensaje', response.data)

    def test_restablecer_password_flujo_completo(self):
        uid = urlsafe_base64_encode(force_bytes(self.cliente_user.pk))
        token = default_token_generator.make_token(self.cliente_user)

        payload = {
            'uid': uid,
            'token': token,
            'password': 'NuevaPassword2026!'
        }
        response = self.client.post('/api/usuarios/restablecer-password/', payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que la nueva contraseña funciona en login
        captcha_key, captcha_val = generar_captcha_para_test()
        login_res = self.client.post('/api/usuarios/login/', {
            'username': 'carlos_cliente',
            'password': 'NuevaPassword2026!',
            'captcha_key': captcha_key,
            'captcha_value': captcha_val
        })
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)

    def test_restablecer_password_token_invalido(self):
        uid = urlsafe_base64_encode(force_bytes(self.cliente_user.pk))
        payload = {
            'uid': uid,
            'token': 'token-falso-invalido',
            'password': 'NuevaPassword2026!'
        }
        response = self.client.post('/api/usuarios/restablecer-password/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_google_login_debug_simulation(self):
        payload = {
            'credential': 'demo-google-token:usuario.google@gmail.com'
        }
        response = self.client.post('/api/usuarios/google-login/', payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['usuario']['email'], 'usuario.google@gmail.com')
        self.assertTrue(Usuario.objects.filter(email='usuario.google@gmail.com').exists())

    def test_actualizar_perfil_usuario(self):
        self.client.force_authenticate(user=self.cliente_user)
        payload = {
            'first_name': 'Carlos Alberto',
            'last_name': 'Huanca Quispe',
            'celular': '984998877',
            'distrito': 'San Sebastián'
        }
        response = self.client.patch('/api/usuarios/perfil/', payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cliente_user.refresh_from_db()
        self.assertEqual(self.cliente_user.first_name, 'Carlos Alberto')
        self.assertEqual(self.cliente_user.celular, '984998877')
        self.assertEqual(self.cliente_user.distrito, 'San Sebastián')

    def test_actualizar_perfil_rol_tampering_bloqueado(self):
        self.client.force_authenticate(user=self.cliente_user)
        payload = {
            'first_name': 'Carlos',
            'rol': 'admin'  # Intento malicioso de escalada de privilegios
        }
        response = self.client.patch('/api/usuarios/perfil/', payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cliente_user.refresh_from_db()
        self.assertEqual(self.cliente_user.rol, 'cliente')  # El rol no debe cambiar

    def test_cambiar_password_exitoso(self):
        self.client.force_authenticate(user=self.cliente_user)
        payload = {
            'password_actual': 'Password123!',
            'password_nueva': 'NuevaClaveSegura2026!'
        }
        response = self.client.post('/api/usuarios/cambiar-password/', payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cliente_user.refresh_from_db()
        self.assertTrue(self.cliente_user.check_password('NuevaClaveSegura2026!'))

    def test_cambiar_password_actual_incorrecta(self):
        self.client.force_authenticate(user=self.cliente_user)
        payload = {
            'password_actual': 'ClaveEquivocada!',
            'password_nueva': 'NuevaClaveSegura2026!'
        }
        response = self.client.post('/api/usuarios/cambiar-password/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_subir_foto_usuario_valida(self):
        self.client.force_authenticate(user=self.cliente_user)
        # Crear imagen real en memoria con Pillow
        img = Image.new('RGB', (100, 100), color='blue')
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        img_file = SimpleUploadedFile("avatar.jpg", img_io.getvalue(), content_type="image/jpeg")

        response = self.client.post('/api/usuarios/foto/', {'foto': img_file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cliente_user.refresh_from_db()
        self.assertTrue(bool(self.cliente_user.foto))
