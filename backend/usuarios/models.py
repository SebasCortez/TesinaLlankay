from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    ROLES = [
        ('cliente', 'Cliente'),
        ('trabajador', 'Trabajador'),
        ('admin', 'Administrador'),
    ]

    rol = models.CharField(max_length=20, choices=ROLES, default='cliente')
    celular = models.CharField(max_length=20, blank=True)
    distrito = models.CharField(max_length=100, blank=True)
    foto = models.ImageField(upload_to='fotos/', blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.rol})"