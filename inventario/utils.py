# inventario/utils.py
import uuid
import re
from django.utils.text import slugify

def generar_codigo_activo(tipo_dispositivo_nombre):
    """
    Genera un código de activo simple basado en el tipo de dispositivo 
    y un identificador único.

    Ejemplo: Laptop -> LAPT-XXXXXX
    """
    if not tipo_dispositivo_nombre:
        return None

    # 1. Obtener un prefijo corto (ej. LAPT, MONT, SERV)
    # Se toman las primeras 4 letras en mayúsculas del nombre slugificado
    prefijo = slugify(tipo_dispositivo_nombre).upper()[:4]

    # 2. Generar un identificador aleatorio corto (ej. 6 caracteres)
    # Se usa la mitad de un UUID y se convierte a base 16 (hex)
    identificador = str(uuid.uuid4().hex)[:6].upper()

    return f"{prefijo}-{identificador}"


def limpiar_nombre_archivo(instance, filename):
    """
    Función de utilidad para nombrar los archivos subidos (ej. imágenes de productos).
    Asegura un nombre de archivo seguro y único.

    Se utiliza como valor del argumento 'upload_to' en ImageField/FileField.
    """
    # Define la carpeta de destino basada en la app
    folder = 'productos' 

    # 1. Limpiar el nombre base del archivo
    # Remueve caracteres especiales y espacios
    filename_base, filename_ext = os.path.splitext(filename)
    safe_filename = slugify(filename_base)
    
    # 2. Asegurar que el nombre del archivo sea único usando el serial del elemento
    if instance.serial:
        unique_name = f"{instance.serial}-{safe_filename}"
    else:
        # Si el serial no existe, usa un UUID para asegurar unicidad
        unique_name = f"{uuid.uuid4().hex}-{safe_filename}"

    # 3. Retornar la ruta completa
    return f"{folder}/{unique_name}{filename_ext.lower()}"