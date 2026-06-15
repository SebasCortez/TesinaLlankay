from django.db import models
from usuarios.models import Usuario
from trabajadores.models import Trabajador

class Calificacion(models.Model):
    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE, related_name='calificaciones')
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='calificaciones_dadas')
    puntuacion = models.IntegerField(choices=[(i,i) for i in range(1,6)])
    comentario = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('trabajador', 'cliente')

    def __str__(self):
        return f"{self.cliente} → {self.trabajador} ({self.puntuacion}⭐)"