from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('registro/', views.registro, name='usuario_registro'),
    path('login/', views.login, name='usuario_login'),
    path('captcha/', views.obtener_captcha, name='usuario_captcha'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('perfil/', views.perfil, name='usuario_perfil'),
    path('foto/', views.subir_foto_usuario, name='usuario_subir_foto'),
    path('cambiar-password/', views.cambiar_password, name='usuario_cambiar_password'),
    path('recuperar-password/', views.recuperar_password, name='usuario_recuperar_password'),
    path('restablecer-password/', views.restablecer_password, name='usuario_restablecer_password'),
    path('google-login/', views.google_login, name='usuario_google_login'),
    path('reset-admin/', views.reset_admin, name='usuario_reset_admin'),
]