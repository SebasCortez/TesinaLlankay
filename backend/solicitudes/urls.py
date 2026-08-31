from django.urls import path
from . import views

urlpatterns = [
    path('', views.mis_solicitudes),
    path('crear/', views.crear_solicitud),
    path('<int:pk>/estado/', views.actualizar_estado),
    path('requerimientos/crear/', views.crear_requerimiento_oficio),
    path('requerimientos/admin/', views.listar_requerimientos_admin),
    path('requerimientos/admin/<int:pk>/', views.actualizar_requerimiento_admin),
]