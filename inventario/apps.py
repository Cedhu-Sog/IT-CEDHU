# inventario/apps.py
from django.apps import AppConfig

class InventarioConfig(AppConfig):
    """
    Clase de configuración para la aplicación 'inventario'.
    """
    # Define el tipo de campo automático por defecto
    default_auto_field = 'django.db.models.BigAutoField'
    
    # Nombre de la aplicación (debe coincidir con el nombre de la carpeta)
    name = 'inventario'
    
    # Nombre visible en el panel de administración de Django
    verbose_name = 'Gestión de Inventario Tecnológico'