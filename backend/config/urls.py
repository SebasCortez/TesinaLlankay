from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/usuarios/', include('usuarios.urls')),
    path('api/trabajadores/', include('trabajadores.urls')),
    path('api/calificaciones/', include('calificaciones.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)   