# usuarios/apps.py
from django.apps import AppConfig

class UsuariosConfig(AppConfig):
    """
    Clase de configuración para la aplicación 'usuarios'.
    """
    # Define el tipo de campo automático por defecto (buena práctica)
    default_auto_field = 'django.db.models.BigAutoField'
    
    # Nombre de la aplicación (debe coincidir con el nombre de la carpeta)
    name = 'usuarios'
    
    # Nombre visible en el panel de administración de Django (opcional)
    verbose_name = 'Gestión de Usuarios'