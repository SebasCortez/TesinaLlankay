from django.urls import path
from . import views

urlpatterns = [
    path('', views.mis_solicitudes),
    path('crear/', views.crear_solicitud),
    path('<int:pk>/estado/', views.actualizar_estado),
]