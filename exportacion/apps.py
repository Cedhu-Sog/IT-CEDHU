# exportacion/apps.py
from django.apps import AppConfig

class ExportacionConfig(AppConfig):
    """
    Clase de configuración para la aplicación 'exportacion'.
    """
    # Define el tipo de campo automático por defecto
    default_auto_field = 'django.db.models.BigAutoField'
    
    # Nombre de la aplicación (debe coincidir con el nombre de la carpeta)
    name = 'exportacion'
    
    # Nombre visible en el panel de administración de Django
    verbose_name = 'Exportación de Datos'