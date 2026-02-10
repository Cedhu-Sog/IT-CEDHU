# exportacion/views.py
import os
import shutil
import datetime
import subprocess
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, FileResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.views.generic import View
from django.conf import settings 
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.management import call_command
import json

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
# 2. Vistas de Gestión de Base de Datos (BD) - ADAPTADO PARA POSTGRESQL
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
    Genera un respaldo de la base de datos PostgreSQL usando pg_dump y lo envía para su descarga.
    NUEVO: Adaptado para PostgreSQL.
    """
    # 1. Verificar Permisos
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, "Permiso denegado.")
        return redirect('inventario:dashboard') 
        
    # 2. Obtener configuración de la base de datos desde settings
    db_config = settings.DATABASES['default']
    db_name = db_config['NAME']
    db_user = db_config['USER']
    db_password = db_config['PASSWORD']
    db_host = db_config['HOST']
    db_port = db_config['PORT']
    
    # 3. Crear carpeta de respaldo
    backup_dir = settings.BASE_DIR.parent / "Base de Datos - Inventario" 
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        
    # 4. Generar nombre del archivo de respaldo
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"inventario_db_backup_{timestamp}.sql"
    backup_path = backup_dir / backup_filename
    
    # 5. Ejecutar pg_dump para crear el respaldo
    try:
        # Configurar la variable de entorno PGPASSWORD para autenticación
        env = os.environ.copy()
        env['PGPASSWORD'] = db_password
        
        # Comando pg_dump - Formato SQL plano
        command = [
            'pg_dump',
            '-h', db_host,
            '-p', str(db_port),
            '-U', db_user,
            '--format=plain',  # Formato SQL plano (legible)
            '--encoding=UTF8',  # Asegurar codificación UTF-8
            '--file=' + str(backup_path),
            db_name
        ]
        
        # Ejecutar el comando
        result = subprocess.run(
            command,
            env=env,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            messages.error(request, f"Error al crear el respaldo: {result.stderr}")
            return redirect('exportacion:gestion_bd')
            
    except FileNotFoundError:
        messages.error(request, "pg_dump no encontrado. Asegúrese de que PostgreSQL esté instalado y en el PATH del sistema.")
        return redirect('exportacion:gestion_bd')
    except Exception as e:
        messages.error(request, f"Error al crear la copia de respaldo: {e}")
        return redirect('exportacion:gestion_bd')
    
    # 6. Enviar el archivo para su descarga
    try:
        response = FileResponse(open(backup_path, 'rb'), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{backup_filename}"'
        messages.success(request, f"Respaldo '{backup_filename}' creado exitosamente.")
        return response
    except Exception as e:
        messages.error(request, f"Error al enviar el archivo: {e}")
        return redirect('exportacion:gestion_bd')


class CargarBDView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Maneja la subida (GET) y el reemplazo (POST) de un respaldo de PostgreSQL.
    NUEVO: Adaptado para PostgreSQL usando pg_restore.
    """
    def test_func(self):
        # Limita esta función a Superusuarios por extrema seguridad (reemplaza la BD)
        return self.request.user.is_superuser

    def get(self, request):
        """Muestra el formulario de carga."""
        form = CargarBDForm()
        messages.warning(request, "¡ADVERTENCIA! Cargar una base de datos reemplazará todos los datos actuales. Asegúrate de tener un respaldo reciente antes de proceder.")
        return render(request, 'exportacion/cargar_bd.html', {'form': form})

    def post(self, request):
        """Procesa la subida del archivo de respaldo."""
        form = CargarBDForm(request.POST, request.FILES)
        
        if form.is_valid():
            uploaded_file = request.FILES['archivo_bd']
            
            # Guardar el archivo temporalmente
            temp_dir = settings.BASE_DIR / 'temp_backups'
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
                
            temp_path = temp_dir / uploaded_file.name
            
            try:
                # Guardar el archivo subido
                with open(temp_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)
                
                # Obtener configuración de la base de datos
                db_config = settings.DATABASES['default']
                db_name = db_config['NAME']
                db_user = db_config['USER']
                db_password = db_config['PASSWORD']
                db_host = db_config['HOST']
                db_port = db_config['PORT']
                
                # Configurar variable de entorno para password
                env = os.environ.copy()
                env['PGPASSWORD'] = db_password
                
                # Nota: Para DROP/CREATE necesitamos conectarnos como superusuario
                # Usaremos el usuario configurado, pero si falla, informaremos al usuario
                
                try:
                    # Primero intentar terminar conexiones activas
                    terminate_command = [
                        'psql', '-h', db_host, '-p', str(db_port), '-U', db_user, '-d', 'postgres',
                        '-c', f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{db_name}';"
                    ]
                    subprocess.run(terminate_command, env=env, capture_output=True)
                    
                    # Ejecutar DROP
                    drop_command = [
                        'psql', '-h', db_host, '-p', str(db_port), '-U', db_user, '-d', 'postgres', 
                        '-c', f'DROP DATABASE IF EXISTS {db_name};'
                    ]
                    subprocess.run(drop_command, env=env, check=True, capture_output=True)
                    
                    # Ejecutar CREATE
                    create_command = [
                        'psql', '-h', db_host, '-p', str(db_port), '-U', db_user, '-d', 'postgres',
                        '-c', f"CREATE DATABASE {db_name} WITH ENCODING 'UTF8' OWNER {db_user};"
                    ]
                    subprocess.run(create_command, env=env, check=True, capture_output=True)
                    
                except subprocess.CalledProcessError as e:
                    # Si el usuario no tiene permisos, sugerir usar postgres
                    os.remove(temp_path)
                    messages.error(request, 
                        f"Error: El usuario '{db_user}' no tiene permisos para eliminar/crear bases de datos. "
                        "Por favor, contacte al administrador del sistema para realizar esta operación, "
                        "o use el usuario 'postgres' en la configuración temporalmente."
                    )
                    return render(request, 'exportacion/cargar_bd.html', {'form': form})
                
                # Restaurar el respaldo usando psql (para archivos SQL planos)
                restore_command = [
                    'psql',
                    '-h', db_host,
                    '-p', str(db_port),
                    '-U', db_user,
                    '-d', db_name,
                    '-f', str(temp_path)  # -f para ejecutar archivo SQL
                ]
                
                result = subprocess.run(
                    restore_command,
                    env=env,
                    capture_output=True,
                    text=True
                )
                
                # Limpiar archivo temporal
                os.remove(temp_path)
                
                # Verificar resultado
                if result.returncode != 0:
                    messages.error(request, f"Error al restaurar la base de datos: {result.stderr}")
                    return render(request, 'exportacion/cargar_bd.html', {'form': form})
                else:
                    messages.success(request, "¡Base de datos restaurada exitosamente! Por favor, reinicie el servidor si es necesario.")
                
                return redirect('exportacion:gestion_bd')

            except subprocess.CalledProcessError as e:
                messages.error(request, f"Error al restaurar la base de datos: {e}")
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return render(request, 'exportacion/cargar_bd.html', {'form': form})
                
            except FileNotFoundError:
                messages.error(request, "psql no encontrado. Asegúrese de que PostgreSQL esté instalado y en el PATH del sistema.")
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return render(request, 'exportacion/cargar_bd.html', {'form': form})
                
            except Exception as e:
                messages.error(request, f"Error al procesar el archivo: {e}")
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return render(request, 'exportacion/cargar_bd.html', {'form': form})
        
        else:
            messages.error(request, "Error de validación del formulario. Asegúrese de seleccionar un archivo .sql válido.")
            return render(request, 'exportacion/cargar_bd.html', {'form': form})