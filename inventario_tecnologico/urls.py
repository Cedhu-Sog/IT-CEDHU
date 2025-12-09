# inventario_tecnologico/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# Importamos una vista genérica para el dashboard si no la tenemos en inventario.
# Si tienes una vista específica para el inicio, puedes importarla aquí. 
# Por ahora, asumiremos que el home principal lo maneja 'inventario'.

urlpatterns = [
    # Ruta de administración de Django
    path('admin/', admin.site.urls),

    # Rutas para la gestión de usuarios (registro, login, perfil)
    path('usuarios/', include('usuarios.urls')),
    
    # Rutas principales del inventario (CRUD, listas)
    path('inventario/', include('inventario.urls')),
    
    # Rutas para la exportación de datos
    path('exportacion/', include('exportacion.urls')),
    
    # Ruta principal (dashboard/home). 
    # Se dirige a la app 'inventario' para manejar la vista de inicio del dashboard.
    path('', include('inventario.urls')), 
]

# Configuración para servir archivos subidos (MEDIA) en modo de desarrollo.
# Esto es necesario para que las imágenes de productos se muestren correctamente.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)