from django.urls import path
from trabajadores import views as tv
from usuarios import views as uv
from solicitudes import views as sv

urlpatterns = [
    path('trabajadores/', tv.admin_listar_trabajadores),
    path('clientes/', uv.admin_listar_clientes),
    path('solicitudes/', sv.admin_listar_solicitudes),
]