from django.db import models
from django.conf import settings

class Notificacion(models.Model):
    TIPO_CHOICES = [
        ('solicitud_nueva', 'Nueva Solicitud'),
        ('solicitud_aceptada', 'Solicitud Aceptada'),
        ('solicitud_en_progreso', 'Solicitud en Progreso'),
        ('solicitud_completada', 'Solicitud Completada'),
        ('solicitud_rechazada', 'Solicitud Rechazada'),
        ('calificacion_recibida', 'Calificación Recibida'),
        ('general', 'General'),
    ]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notificaciones')
    titulo = models.CharField(max_length=150)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES, default='general')
    leida = models.BooleanField(default=False)
    enlace = models.CharField(max_length=200, blank=True, default='/solicitudes')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.usuario.username} - {self.titulo} ({'Leída' if self.leida else 'No leída'})"

def crear_notificacion(usuario, titulo, mensaje, tipo='general', enlace='/solicitudes'):
    """Helper para crear notificaciones de forma segura y rápida en cualquier vista"""
    if usuario:
        return Notificacion.objects.create(
            usuario=usuario,
            titulo=titulo,
            mensaje=mensaje,
            tipo=tipo,
            enlace=enlace
        )
    return None
