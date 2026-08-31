from django.contrib import admin
from .models import Solicitud, RequerimientoOficio

@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'trabajador', 'estado', 'fecha_solicitud')
    list_filter = ('estado', 'fecha_solicitud')
    search_fields = ('cliente__username', 'trabajador__usuario__username', 'mensaje', 'descripcion_problema')

@admin.register(RequerimientoOficio)
class RequerimientoOficioAdmin(admin.ModelAdmin):
    list_display = ('id', 'oficio_solicitado', 'nombre_contacto', 'celular_contacto', 'distrito', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'distrito', 'fecha_creacion')
    search_fields = ('oficio_solicitado', 'nombre_contacto', 'celular_contacto', 'descripcion')
