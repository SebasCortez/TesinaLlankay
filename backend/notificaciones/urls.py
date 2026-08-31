from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_notificaciones, name='listar_notificaciones'),
    path('<int:pk>/leer/', views.marcar_leida, name='marcar_leida'),
    path('marcar-todas-leidas/', views.marcar_todas_leidas, name='marcar_todas_leidas'),
]
