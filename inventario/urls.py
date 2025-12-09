# inventario/urls.py
from django.urls import path
from . import views

# Define el namespace de la aplicación
app_name = 'inventario'

urlpatterns = [
    # 1. Dashboard / Página principal
    # Esta ruta es la que se mapea a la raíz del proyecto ('/') en el urls.py principal
    path('', views.DashboardView.as_view(), name='dashboard'), 

    # 2. Vistas CRUD de Elementos
    
    # Listar todos los elementos
    path('lista/', views.ListaInventarioView.as_view(), name='lista_inventario'),
    
    # Crear nuevo elemento
    path('anadir/', views.ElementoCreateView.as_view(), name='anadir_elemento'),
    
    # Ver detalle de un elemento específico (usa su PK)
    path('ver/<int:pk>/', views.DetalleElementoView.as_view(), name='ver_elemento'),
    
    # Editar un elemento específico (usa su PK)
    path('editar/<int:pk>/', views.ElementoUpdateView.as_view(), name='editar_elemento'),
    
    # Eliminar un elemento específico (usa su PK)
    path('eliminar/<int:pk>/', views.ElementoDeleteView.as_view(), name='eliminar_elemento'),
]