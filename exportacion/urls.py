# exportacion/urls.py
from django.urls import path
from . import views

# Define el namespace de la aplicación
app_name = 'exportacion'

urlpatterns = [
    # Muestra las opciones de exportación y maneja el inicio de la solicitud GET
    path('opciones/', views.opciones_exportacion, name='opciones_exportacion'),
    
    # Rutas directas para la generación de archivos (generalmente llamadas desde opciones_exportacion)
    # Estas se mantienen separadas por si se necesita llamarlas vía AJAX en el futuro.
    
    path('excel/', views.exportar_inventario_excel, name='exportar_excel'),
    path('pdf/', views.exportar_inventario_pdf, name='exportar_pdf'),

    path('gestion-bd/', views.GestionBDView.as_view(), name='gestion_bd'), # Nueva vista para mostrar opciones
    path('descargar-bd/', views.descargar_base_datos, name='descargar_bd'), # Nueva función para descargar
    path('cargar-bd/', views.CargarBDView.as_view(), name='cargar_bd'), # Nueva vista para cargar
]