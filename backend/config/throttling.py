from rest_framework.throttling import SimpleRateThrottle, AnonRateThrottle, UserRateThrottle


class LoginRateThrottle(SimpleRateThrottle):
    """
    Limita los intentos de inicio de sesión a 5 por minuto por IP para prevenir ataques de fuerza bruta.
    """
    scope = 'login'

    def get_cache_key(self, request, view):
        ident = self.get_ident(request)
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class RegistroRateThrottle(SimpleRateThrottle):
    """
    Limita la creación de nuevas cuentas a 10 por hora por IP para prevenir spam.
    """
    scope = 'registro'

    def get_cache_key(self, request, view):
        ident = self.get_ident(request)
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class PasswordResetRateThrottle(SimpleRateThrottle):
    """
    Limita las solicitudes de recuperación de contraseña a 5 por hora por IP para evitar flooding de emails.
    """
    scope = 'recuperar_password'

    def get_cache_key(self, request, view):
        ident = self.get_ident(request)
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class AgenteChatRateThrottle(SimpleRateThrottle):
    """
    Limita las consultas al agente conversacional a 15 por minuto por IP/Usuario.
    """
    scope = 'agente_chat'

    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            ident = f"user_{request.user.pk}"
        else:
            ident = f"ip_{self.get_ident(request)}"

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class SolicitudRateThrottle(SimpleRateThrottle):
    """
    Limita la creación de solicitudes de servicio a 30 por hora por usuario autenticado.
    """
    scope = 'solicitud'

    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            ident = f"user_{request.user.pk}"
        else:
            ident = f"ip_{self.get_ident(request)}"

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }
