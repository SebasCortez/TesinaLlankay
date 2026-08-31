from django.core.management.base import BaseCommand
from django.utils import timezone
from usuarios.models import Usuario
from trabajadores.models import Trabajador
from calificaciones.models import Calificacion
from solicitudes.models import Solicitud
from notificaciones.models import Notificacion

class Command(BaseCommand):
    help = 'Puebla la base de datos con datos cusqueños de prueba realistas para demostración y evaluación.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limpiar',
            action='store_true',
            help='Elimina datos existentes de prueba antes de poblar.',
        )

    def handle(self, *args, **options):
        if options['limpiar']:
            self.stdout.write(self.style.WARNING('Limpiando base de datos...'))
            Solicitud.objects.all().delete()
            Calificacion.objects.all().delete()
            Notificacion.objects.all().delete()
            Trabajador.objects.all().delete()
            Usuario.objects.exclude(username='admin').delete()
            self.stdout.write(self.style.SUCCESS('Base de datos limpiada.'))

        # 1. Crear Administrador
        admin_user, created = Usuario.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@llankay.pe',
                'first_name': 'Admin',
                'last_name': 'Llankay',
                'rol': 'admin',
                'celular': '984000111',
                'distrito': 'Cusco',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('Admin123!')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('[OK] Superusuario admin creado (Pass: Admin123!)'))

        # 2. Crear Clientes de demostración
        clientes_data = [
            {
                'username': 'cliente_cusco',
                'email': 'carlos.huanca@gmail.com',
                'first_name': 'Carlos',
                'last_name': 'Huanca',
                'rol': 'cliente',
                'celular': '984112233',
                'distrito': 'Wanchaq'
            },
            {
                'username': 'maria_cliente',
                'email': 'maria.quispe@hotmail.com',
                'first_name': 'María Elena',
                'last_name': 'Quispe Mamani',
                'rol': 'cliente',
                'celular': '984556677',
                'distrito': 'Cusco'
            }
        ]

        clientes_objs = []
        for c_data in clientes_data:
            user, c_created = Usuario.objects.get_or_create(
                username=c_data['username'],
                defaults=c_data
            )
            if c_created:
                user.set_password('Password123!')
                user.save()
            clientes_objs.append(user)

        self.stdout.write(self.style.SUCCESS(f'[OK] {len(clientes_objs)} clientes creados'))

        # 3. Datos de Técnicos en Cusco
        tecnicos_data = [
            {
                'username': 'juan_electricista',
                'first_name': 'Juan Carlos',
                'last_name': 'Paucar Condori',
                'email': 'juan.electricista@gmail.com',
                'celular': '984223344',
                'distrito': 'Wanchaq',
                'categoria': 'Electricidad',
                'oficio': 'Electricista Matriculado y Tableros',
                'experiencia': 'Más de 5 años',
                'descripcion': 'Especialista en instalaciones eléctricas residenciales y comerciales, reparación de cortocircuitos, cableado estructurado y pozos a tierra con certificación en Cusco.',
                'latitud': -13.5250,
                'longitud': -71.9500,
                'disponible': True,
                'calif': 4.9,
                'num_calif': 14
            },
            {
                'username': 'raul_gasfitero',
                'first_name': 'Raúl',
                'last_name': 'Aparicio Huamán',
                'email': 'raul.termas@gmail.com',
                'celular': '984334455',
                'distrito': 'San Sebastián',
                'categoria': 'Gasfitería',
                'oficio': 'Técnico Especialista en Termas Solares y a Gas',
                'experiencia': 'Más de 5 años',
                'descripcion': 'Instalación y mantenimiento preventivo de termas solares, eléctricas y a gas. Detección y solución de fugas de agua sin romper paredes. Destape de desagües con máquina.',
                'latitud': -13.5330,
                'longitud': -71.9280,
                'disponible': True,
                'calif': 4.8,
                'num_calif': 19
            },
            {
                'username': 'mario_carpintero',
                'first_name': 'Mario',
                'last_name': 'Ccarhuas Ttito',
                'email': 'mario.muebles@gmail.com',
                'celular': '984445566',
                'distrito': 'Cusco',
                'categoria': 'Carpintería',
                'oficio': 'Carpintero Ebanista y Restaurador',
                'experiencia': 'Más de 5 años',
                'descripcion': 'Fabricación de muebles a medida en melamine y madera fina (cedro, aguano). Mantenimiento de puertas coloniales, closets, reposteros de cocina y pisos de parquet en Cusco.',
                'latitud': -13.5140,
                'longitud': -71.9750,
                'disponible': True,
                'calif': 4.9,
                'num_calif': 11
            },
            {
                'username': 'cesar_cerrajero',
                'first_name': 'César',
                'last_name': 'Valenzuela Choque',
                'email': 'cesar.cerrajero24h@gmail.com',
                'celular': '984667788',
                'distrito': 'Cusco',
                'categoria': 'Cerrajería',
                'oficio': 'Cerrajería Integral de Emergencia 24 Horas',
                'experiencia': '3-5 años',
                'descripcion': 'Apertura urgente de puertas de casas, departamentos y cajas fuertes. Instalación de cerraduras digitales con huella digital, cerrojos de alta seguridad Cantol y Yale.',
                'latitud': -13.5180,
                'longitud': -71.9780,
                'disponible': True,
                'calif': 4.7,
                'num_calif': 22
            },
            {
                'username': 'luis_pintor',
                'first_name': 'Luis Alberto',
                'last_name': 'Yabar Mendoza',
                'email': 'luis.pinturas@gmail.com',
                'celular': '984778899',
                'distrito': 'Santiago',
                'categoria': 'Pintura',
                'oficio': 'Pintor de Interiores, Fachadas y Empastados',
                'experiencia': '3-5 años',
                'descripcion': 'Pintura satinada, látex y esmalte de primera calidad. Tratamiento contra salitre y humedad típica del clima cusqueño. Acabados finos en yeso y drywall.',
                'latitud': -13.5280,
                'longitud': -71.9850,
                'disponible': False,
                'calif': 4.6,
                'num_calif': 8
            },
            {
                'username': 'gabriel_electricista',
                'first_name': 'Gabriel',
                'last_name': 'Flores Zúñiga',
                'email': 'gabriel.electrico@gmail.com',
                'celular': '984889900',
                'distrito': 'Wanchaq',
                'categoria': 'Electricidad',
                'oficio': 'Técnico Electricista e Iluminación LED',
                'experiencia': '1-3 años',
                'descripcion': 'Diseño e instalación de iluminación decorativa LED, reflectores solares, cambio de térmicas, cableados y mantenimiento de bombas eléctricas de agua.',
                'latitud': -13.5200,
                'longitud': -71.9450,
                'disponible': True,
                'calif': 4.5,
                'num_calif': 6
            },
            {
                'username': 'fernando_gasfitero',
                'first_name': 'Fernando',
                'last_name': 'Molina Baca',
                'email': 'fernando.gasfitero@gmail.com',
                'celular': '984990011',
                'distrito': 'San Jerónimo',
                'categoria': 'Gasfitería',
                'oficio': 'Instalador Sanitario y Bombas de Presión',
                'experiencia': '3-5 años',
                'descripcion': 'Instalación de redes de agua fría y caliente en termofusión PPR. Montaje de bombas hidroneumáticas, tanques Rotoplas y griferías monocomando.',
                'latitud': -13.5450,
                'longitud': -71.8900,
                'disponible': True,
                'calif': 4.8,
                'num_calif': 12
            },
            {
                'username': 'rodrigo_carpintero',
                'first_name': 'Rodrigo',
                'last_name': 'Alvarez Quispe',
                'email': 'rodrigo.melamine@gmail.com',
                'celular': '984123987',
                'distrito': 'San Sebastián',
                'categoria': 'Carpintería',
                'oficio': 'Especialista en Drywall y Melamina',
                'experiencia': '3-5 años',
                'descripcion': 'Divisiones y techos de drywall resistentes a la humedad, cielo raso PVC, reposteros modernos con cantos gruesos y cajoneras con correderas telescópicas.',
                'latitud': -13.5300,
                'longitud': -71.9350,
                'disponible': True,
                'calif': 4.7,
                'num_calif': 9
            },
            {
                'username': 'pedro_cerrajero',
                'first_name': 'Pedro',
                'last_name': 'Ochoa Cardenas',
                'email': 'pedro.cerrajeria@gmail.com',
                'celular': '984234876',
                'distrito': 'Wanchaq',
                'categoria': 'Cerrajería',
                'oficio': 'Cerrajería Residencial y Duplicado de Llaves',
                'experiencia': 'Más de 5 años',
                'descripcion': 'Aperturas de autos y chapas de seguridad. Fabricación e instalación de rejas de fierro forjado, portones levadizos y cambio de combinación.',
                'latitud': -13.5230,
                'longitud': -71.9600,
                'disponible': True,
                'calif': 4.9,
                'num_calif': 16
            },
            {
                'username': 'diego_pintor',
                'first_name': 'Diego',
                'last_name': 'Castelo Soto',
                'email': 'diego.pintor@gmail.com',
                'celular': '984345765',
                'distrito': 'San Jerónimo',
                'categoria': 'Pintura',
                'oficio': 'Pintor Decorativo y Microcemento',
                'experiencia': '1-3 años',
                'descripcion': 'Aplicación de microcemento decorativo para baños y cocinas, efectos de estuco veneciano, lacado de maderas y protección de muros de adobe y piedra.',
                'latitud': -13.5120,
                'longitud': -71.9720,
                'disponible': True,
                'calif': 4.6,
                'num_calif': 7
            }
        ]

        trabajadores_creados = []
        for t_info in tecnicos_data:
            user, u_created = Usuario.objects.get_or_create(
                username=t_info['username'],
                defaults={
                    'first_name': t_info['first_name'],
                    'last_name': t_info['last_name'],
                    'email': t_info['email'],
                    'celular': t_info['celular'],
                    'distrito': t_info['distrito'],
                    'rol': 'trabajador'
                }
            )
            if u_created:
                user.set_password('Password123!')
                user.save()

            trabajador, trab_created = Trabajador.objects.get_or_create(
                usuario=user,
                defaults={
                    'categoria': t_info['categoria'],
                    'oficio': t_info['oficio'],
                    'experiencia': t_info['experiencia'],
                    'descripcion': t_info['descripcion'],
                    'latitud': t_info['latitud'],
                    'longitud': t_info['longitud'],
                    'disponible': t_info['disponible'],
                    'estado': 'aprobado',
                    'calificacion_promedio': t_info['calif'],
                    'num_calificaciones': t_info['num_calif'],
                    'fecha_aprobacion': timezone.now()
                }
            )
            trabajadores_creados.append(trabajador)

        self.stdout.write(self.style.SUCCESS(f'[OK] {len(trabajadores_creados)} tecnicos cusquenos aprobados creados'))

        # 4. Crear Reseñas y Calificaciones Realistas
        califs_ejemplo = [
            {'puntuacion': 5, 'comentario': 'Excelente trabajo con la terma solar, vino puntual a San Sebastián y solucionó la fuga de inmediato. 100% recomendado.', 'cliente': clientes_objs[0], 'trab': trabajadores_creados[1]},
            {'puntuacion': 5, 'comentario': 'Instaló el tablero general de mi departamento en Wanchaq con materiales de calidad. Muy profesional y respetuoso.', 'cliente': clientes_objs[1], 'trab': trabajadores_creados[0]},
            {'puntuacion': 4, 'comentario': 'Rápido servicio para abrir la puerta de mi casa un domingo por la noche. Precio justo.', 'cliente': clientes_objs[0], 'trab': trabajadores_creados[3]},
            {'puntuacion': 5, 'comentario': 'Restauró una puerta colonial antigua dejándola como nueva. Gran maestro carpintero.', 'cliente': clientes_objs[1], 'trab': trabajadores_creados[2]},
        ]

        for c_item in califs_ejemplo:
            Calificacion.objects.get_or_create(
                trabajador=c_item['trab'],
                cliente=c_item['cliente'],
                defaults={
                    'puntuacion': c_item['puntuacion'],
                    'comentario': c_item['comentario']
                }
            )

        self.stdout.write(self.style.SUCCESS('[OK] Resenas y calificaciones de ejemplo creadas'))

        # 5. Crear Solicitudes de Demostración con Presupuestos
        solicitudes_ejemplo = [
            {
                'cliente': clientes_objs[0],
                'trabajador': trabajadores_creados[0],
                'mensaje': 'Hola Juan Carlos, necesito cambiar la llave termomagnética que se baja a cada rato en la cocina.',
                'descripcion_problema': 'Sobrecarga en el circuito de electrodomésticos.',
                'direccion': 'Av. Diagonal Angamos 320, Wanchaq',
                'estado': 'en_progreso',
                'precio_acordado': 60.00,
                'metodo_pago': 'Yape'
            },
            {
                'cliente': clientes_objs[1],
                'trabajador': trabajadores_creados[1],
                'mensaje': 'Buenas tardes, la terma no calienta bien el agua por las mañanas.',
                'descripcion_problema': 'Mantenimiento preventivo de paneles solares y sensor.',
                'direccion': 'Calle Tandapata 140, Cusco',
                'estado': 'aceptado',
                'precio_acordado': 80.00,
                'metodo_pago': 'Plin'
            },
            {
                'cliente': clientes_objs[0],
                'trabajador': trabajadores_creados[2],
                'mensaje': 'Fabricación de un estante para libros en cedro de 1.80m x 1.20m.',
                'descripcion_problema': 'Mueble a medida para sala de estudio.',
                'direccion': 'Urb. Santa Mónica D-4, Wanchaq',
                'estado': 'completado',
                'precio_acordado': 250.00,
                'metodo_pago': 'Efectivo'
            }
        ]

        for s_info in solicitudes_ejemplo:
            Solicitud.objects.get_or_create(
                cliente=s_info['cliente'],
                trabajador=s_info['trabajador'],
                mensaje=s_info['mensaje'],
                defaults=s_info
            )

        self.stdout.write(self.style.SUCCESS('[OK] Solicitudes de prueba con cotizaciones creadas'))

        # 6. Notificaciones de Demostración
        Notificacion.objects.get_or_create(
            usuario=clientes_objs[0],
            titulo="Solicitud Aceptada",
            defaults={
                'mensaje': 'El técnico Juan Carlos Paucar ha aceptado tu solicitud de Electricidad.',
                'tipo': 'solicitud_aceptada',
                'enlace': '/solicitudes'
            }
        )
        Notificacion.objects.get_or_create(
            usuario=trabajadores_creados[0].usuario,
            titulo="Nueva Solicitud de Servicio",
            defaults={
                'mensaje': 'Carlos Huanca te ha enviado una solicitud de Electricidad en Wanchaq.',
                'tipo': 'solicitud_nueva',
                'enlace': '/solicitudes'
            }
        )

        self.stdout.write(self.style.SUCCESS('[OK] Notificaciones en vivo de prueba creadas'))
        self.stdout.write(self.style.SUCCESS('\n======================================================'))
        self.stdout.write(self.style.SUCCESS('POBLACION DE DATOS COMPLETADA CON EXITO'))
        self.stdout.write(self.style.SUCCESS('======================================================'))
        self.stdout.write(self.style.SUCCESS('Cuentas listas para probar:'))
        self.stdout.write(self.style.SUCCESS('  Admin:    admin / Admin123!'))
        self.stdout.write(self.style.SUCCESS('  Cliente:  cliente_cusco / Password123!'))
        self.stdout.write(self.style.SUCCESS('  Tecnico:  juan_electricista / Password123!'))
        self.stdout.write(self.style.SUCCESS('  Tecnico:  raul_gasfitero / Password123!'))
        self.stdout.write(self.style.SUCCESS('======================================================\n'))

