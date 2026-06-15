from django.urls import path
from . import views

urlpatterns = [
    path('', views.crear_calificacion),
    path('<int:trabajador_id>/', views.listar_calificaciones),
]