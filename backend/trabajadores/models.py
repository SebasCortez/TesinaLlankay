from django.db import models
from usuarios.models import Usuario

class Trabajador(models.Model):
    CATEGORIAS = [
        ('Electricidad', 'Electricidad'),
        ('Gasfitería', 'Gasfitería'),
        ('Carpintería', 'Carpintería'),
        ('Cerrajería', 'Cerrajería'),
        ('Pintura', 'Pintura'),
    ]

    EXPERIENCIA = [
        ('Menos de 1 año', 'Menos de 1 año'),
        ('1-3 años', '1-3 años'),
        ('3-5 años', '3-5 años'),
        ('Más de 5 años', 'Más de 5 años'),
    ]

    ESTADO = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]

    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_trabajador')
    categoria = models.CharField(max_length=50, choices=CATEGORIAS)
    oficio = models.CharField(max_length=150)
    experiencia = models.CharField(max_length=50, choices=EXPERIENCIA)
    descripcion = models.TextField(blank=True)
    disponible = models.BooleanField(default=True)
    calificacion_promedio = models.FloatField(default=0.0)
    num_calificaciones = models.IntegerField(default=0)
    latitud = models.FloatField(null=True, blank=True)
    longitud = models.FloatField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO, default='pendiente')
    motivo_rechazo = models.TextField(blank=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.usuario.get_full_name()} — {self.oficio} ({self.estado})"