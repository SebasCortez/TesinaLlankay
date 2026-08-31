from django.db import models
from usuarios.models import Usuario
from trabajadores.models import Trabajador

class Calificacion(models.Model):
    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE, related_name='calificaciones')
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='calificaciones_dadas')
    solicitud = models.ForeignKey('solicitudes.Solicitud', on_delete=models.SET_NULL, null=True, blank=True, related_name='calificacion')
    puntuacion = models.IntegerField(choices=[(i,i) for i in range(1,6)])
    comentario = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"Cliente {self.cliente} → Técnico {self.trabajador} ({self.puntuacion}⭐)"


class CalificacionCliente(models.Model):
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='calificaciones_recibidas')
    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE, related_name='calificaciones_a_clientes')
    solicitud = models.ForeignKey('solicitudes.Solicitud', on_delete=models.SET_NULL, null=True, blank=True, related_name='calificacion_cliente')
    puntuacion = models.IntegerField(choices=[(i,i) for i in range(1,6)])
    comentario = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"Técnico {self.trabajador} → Cliente {self.cliente} ({self.puntuacion}⭐)"