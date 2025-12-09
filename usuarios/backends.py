# usuarios/backends.py
from django.contrib.auth.backends import ModelBackend
from .models import Usuario

class AprobacionRequeridaBackend(ModelBackend):
    """
    Backend de autenticación personalizado que verifica que el usuario
    esté aprobado además de activo antes de permitir el login.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Autentica al usuario solo si está activo Y aprobado.
        """
        try:
            # Busca el usuario por email (nuestro USERNAME_FIELD)
            user = Usuario.objects.get(email=username)
        except Usuario.DoesNotExist:
            return None
        
        # Verifica la contraseña
        if user.check_password(password):
            # Verifica que el usuario esté activo Y aprobado
            if user.is_active and user.is_approved:
                return user
            # Si no está aprobado, retorna None (no permite el login)
            return None
        
        return None
    
    def get_user(self, user_id):
        """
        Obtiene el usuario por ID, solo si está activo y aprobado.
        """
        try:
            user = Usuario.objects.get(pk=user_id)
            if user.is_active and user.is_approved:
                return user
        except Usuario.DoesNotExist:
            return None
        return None