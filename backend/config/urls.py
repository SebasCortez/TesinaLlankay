from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    # OpenAPI & Swagger UI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # APIs
    path('api/usuarios/', include('usuarios.urls')),
    path('api/trabajadores/', include('trabajadores.urls')),
    path('api/calificaciones/', include('calificaciones.urls')),
    path('api/solicitudes/', include('solicitudes.urls')),
    path('api/notificaciones/', include('notificaciones.urls')),
    path('api/agente/', include('servicios.urls')),
    path('api/admin/', include('config.admin_urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

   