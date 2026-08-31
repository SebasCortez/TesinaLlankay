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
    precio_acordado = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    metodo_pago = models.CharField(max_length=30, blank=True, default='Efectivo')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.cliente} → {self.trabajador} ({self.estado})"

class RequerimientoOficio(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('contactado', 'Contactado'),
        ('asignado', 'Técnico asignado'),
        ('atendido', 'Atendido / Completado'),
        ('cancelado', 'Cancelado'),
    ]

    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='requerimientos_oficio')
    nombre_contacto = models.CharField(max_length=100)
    celular_contacto = models.CharField(max_length=15)
    distrito = models.CharField(max_length=100, default='Wanchaq')
    oficio_solicitado = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    notas_admin = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"[{self.estado}] {self.oficio_solicitado} ({self.nombre_contacto} - {self.celular_contacto})"