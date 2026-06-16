from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_trabajadores),
    path('registro/', views.registrar_trabajador),
    path('mi-perfil/', views.mi_perfil_trabajador),
    path('ubicacion/', views.actualizar_ubicacion),
    path('pendientes/', views.listar_pendientes),
    path('<int:pk>/aprobar/', views.aprobar_trabajador),
    path('<int:pk>/rechazar/', views.rechazar_trabajador),
    path('<int:pk>/', views.detalle_trabajador),
    path('disponibilidad/', views.toggle_disponibilidad),
]