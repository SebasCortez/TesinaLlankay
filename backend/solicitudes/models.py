from django.db import models
from usuarios.models import Usuario
from trabajadores.models import Trabajador

class Solicitud(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aceptado', 'Aceptado'),
        ('en_progreso', 'En progreso'),
        ('completado', 'Completado'),
        ('rechazado', 'Rechazado'),
    ]

    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='solicitudes_enviadas')
    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE, related_name='solicitudes_recibidas')
    mensaje = models.TextField()
    descripcion_problema = models.TextField()
    direccion = models.CharField(max_length=255)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    motivo_rechazo = models.TextField(blank=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.cliente} → {self.trabajador} ({self.estado})"