# exportacion/views.py
import os
import shutil
import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, FileResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.views.generic import View
from django.conf import settings 
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

# Importamos la lógica de exportación que crearemos en exporters.py
from .exporters import exportar_a_excel, exportar_a_pdf 
# Importamos el modelo Elemento para obtener los datos
from inventario.models import Elemento 
from .forms import CargarBDForm # Formulario necesario para la carga


# ==============================================================================
# 1. Vistas de Exportación de Inventario (Excel/PDF)
# ==============================================================================

@login_required
def opciones_exportacion(request):
    """
    Muestra la página con opciones para exportar el inventario (template).
    Maneja el formulario GET para iniciar la exportación.
    """
    if request.method == 'GET' and 'formato' in request.GET:
        # Si se envió el formulario GET con un formato, se redirige a la vista de exportación.
        formato = request.GET.get('formato')
        
        # Obtener los elementos. Aquí se podría añadir lógica de filtrado si es necesario.
        elementos = Elemento.objects.all() 
        
        if not elementos.exists():
            messages.warning(request, "No hay elementos en el inventario para exportar.")
            return render(request, 'exportacion/opciones_exportacion.html')

        if formato == 'excel':
            return exportar_inventario_excel(request, elementos)
        elif formato == 'pdf':
            return exportar_inventario_pdf(request, elementos)
        else:
            messages.error(request, "Formato de exportación no válido.")
            
    return render(request, 'exportacion/opciones_exportacion.html')


@login_required
@require_http_methods(["GET"]) # Solo permite peticiones GET
def exportar_inventario_excel(request, elementos=None):
    """
    Función que llama a la utilidad de exportación a Excel y devuelve la respuesta HTTP.
    Esta función helper es llamada desde opciones_exportacion.
    """
    # Si la lista de elementos no se pasa (ej. llamada directa), se obtiene todo el inventario
    if elementos is None:
        elementos = Elemento.objects.all()

    try:
        # La función de utilidad devuelve un HttpResponse
        response = exportar_a_excel(elementos)
        return response
    except Exception as e:
        messages.error(request, f"Error al generar el archivo Excel: {e}")
        return redirect('exportacion:opciones_exportacion')


@login_required
@require_http_methods(["GET"]) # Solo permite peticiones GET
def exportar_inventario_pdf(request, elementos=None):
    """
    Función que llama a la utilidad de exportación a PDF y devuelve la respuesta HTTP.
    Esta función helper es llamada desde opciones_exportacion.
    """
    if elementos is None:
        elementos = Elemento.objects.all()

    try:
        # La función de utilidad devuelve un HttpResponse
        response = exportar_a_pdf(elementos)
        return response
    except Exception as e:
        messages.error(request, f"Error al generar el archivo PDF: {e}")
        return redirect('exportacion:opciones_exportacion')


# ==============================================================================
# 2. Vistas de Gestión de Base de Datos (BD)
# ==============================================================================

class GestionBDView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Muestra la página con opciones para descargar/cargar la BD.
    Solo accesible para usuarios Staff/Superusuarios.
    """
    def test_func(self):
        # Limita esta función a usuarios Staff o Superusuarios por seguridad
        return self.request.user.is_staff or self.request.user.is_superuser

    def get(self, request):
        return render(request, 'exportacion/gestionar_bd.html')


@login_required
@require_http_methods(["GET"])
def descargar_base_datos(request):
    """
    Genera un respaldo del archivo db.sqlite3 y lo envía para su descarga.
    """
    # 1. Verificar Permisos (Doble verificación para vistas basadas en funciones)
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, "Permiso denegado.")
        return redirect('inventario:dashboard') 
        
    # 2. Definir rutas
    # settings.BASE_DIR es la raíz del proyecto (donde está manage.py)
    db_path = settings.BASE_DIR / 'db.sqlite3' 
    # Carpeta de destino (al mismo nivel que BASE_DIR). 
    # Usamos .parent para salir del directorio del proyecto y crear la carpeta de respaldo.
    backup_dir = settings.BASE_DIR.parent / "Base de Datos - Inventario" 
    
    # 3. Crear la carpeta si no existe
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        
    # 4. Generar el nombre del archivo de respaldo
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"inventario_db_backup_{timestamp}.sqlite3"
    backup_path = backup_dir / backup_filename
    
    # 5. Copiar el archivo de la BD al directorio de respaldo
    try:
        shutil.copyfile(db_path, backup_path)
    except FileNotFoundError:
        messages.error(request, "El archivo de base de datos (db.sqlite3) no fue encontrado.")
        return redirect('exportacion:gestion_bd')
    except Exception as e:
        messages.error(request, f"Error al crear la copia de respaldo: {e}")
        return redirect('exportacion:gestion_bd')
    
    # 6. Enviar el archivo para su descarga
    response = FileResponse(open(backup_path, 'rb'), content_type='application/x-sqlite3')
    response['Content-Disposition'] = f'attachment; filename="{backup_filename}"'
    
    messages.success(request, f"Respaldo '{backup_filename}' creado exitosamente en la carpeta externa.")
    return response


class CargarBDView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Maneja la subida (GET) y el reemplazo (POST) del archivo db.sqlite3.
    """
    def test_func(self):
        # Limita esta función a Superusuarios por extrema seguridad (reemplaza la BD)
        return self.request.user.is_superuser

    def get(self, request):
        """Muestra el formulario de carga."""
        form = CargarBDForm()
        messages.warning(request, "¡ADVERTENCIA! Subir una base de datos reemplazará la actual. Asegúrate de tener un respaldo reciente antes de proceder.")
        # Aquí la vista busca 'exportacion/cargar_bd.html'
        return render(request, 'exportacion/cargar_bd.html', {'form': form})

    def post(self, request):
        """Procesa la subida del archivo."""
        form = CargarBDForm(request.POST, request.FILES)
        
        if form.is_valid():
            uploaded_file = request.FILES['archivo_bd']
            db_path = settings.BASE_DIR / 'db.sqlite3'
            
            try:
                # Escribir el contenido del archivo subido en la ubicación de db.sqlite3
                with open(db_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)
                        
                messages.success(request, "¡Base de datos cargada y reemplazada con éxito! Por favor, **reinicie el servidor de Django** para asegurar que los cambios surtan efecto y evitar errores de conexión.")
                return redirect('exportacion:gestion_bd')

            except Exception as e:
                messages.error(request, f"Error al intentar escribir la BD: {e}")
                # Aquí la vista busca 'exportacion/cargar_bd.html'
                return render(request, 'exportacion/cargar_bd.html', {'form': form})
        
        else:
            messages.error(request, "Error de validación del formulario. Asegúrese de seleccionar un archivo .sqlite3 válido.")
            # Aquí la vista busca 'exportacion/cargar_bd.html'
            return render(request, 'exportacion/cargar_bd.html', {'form': form})