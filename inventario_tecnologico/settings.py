sudo systemctl restart gunicorn
sudo systemctl restart nginx
sudo systemctl restart gunicorn
sudo systemctl restart nginx
"""
Configuración de Django para el proyecto inventario_tecnologico.
"""

import os
from pathlib import Path

# Construye rutas dentro del proyecto como esta: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ==============================================================================
# CONFIGURACIÓN DE SEGURIDAD
# ==============================================================================

# ADVERTENCIA: ¡Mantén la clave secreta usada en producción en secreto!
# Por motivos de ejemplo, se usa una clave de desarrollo simple.
# En un proyecto real, esto debe cargarse desde variables de entorno.
import os

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

# Modo de depuración. Desactivar en producción.
DEBUG = False

# Hosts permitidos para servir el proyecto.
ALLOWED_HOSTS = [
    '192.168.1.250',
    '.ngrok-free.dev',
    'overnoble-alessandro-tornly.ngrok-free.dev',
]

CSRF_TRUSTED_ORIGINS = [
    'https://*.ngrok-free.dev'
]


# ==============================================================================
# CONFIGURACIÓN DE APLICACIONES
# ==============================================================================

INSTALLED_APPS = [
    # Apps de Django por defecto
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps de terceros
    'django_filters', # Utilizado en la app 'inventario' para filtros

    # Apps locales del proyecto
    'usuarios',
    'inventario',
    'exportacion',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'inventario_tecnologico.urls'


# ==============================================================================
# CONFIGURACIÓN DE TEMPLATES
# ==============================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Directorio de templates globales (inventario_tecnologico/templates/)
        'DIRS': [os.path.join(BASE_DIR, 'templates')], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'inventario_tecnologico.wsgi.application'
ASGI_APPLICATION = 'inventario_tecnologico.asgi.application'



# ==============================================================================
# CONFIGURACIÓN DE BASE DE DATOS
# ==============================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        # Archivo db.sqlite3 en la raíz del proyecto
        'NAME': BASE_DIR / 'db.sqlite3', 
    }
}


# ==============================================================================
# CONFIGURACIÓN DE AUTENTICACIÓN Y SEGURIDAD
# ==============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Especifica el modelo de usuario personalizado creado en la app 'usuarios'
AUTH_USER_MODEL = 'usuarios.Usuario'

# Redirección tras iniciar sesión y cerrar sesión
LOGIN_URL = 'usuarios:login' # Nombre de la URL para el login
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = 'usuarios:login'


# ==============================================================================
# CONFIGURACIÓN DE INTERNACIONALIZACIÓN
# ==============================================================================

LANGUAGE_CODE = 'es-co' # Colombia (ajustar si es necesario)

TIME_ZONE = 'America/Bogota' # Zona horaria de Colombia (ajustar si es necesario)

USE_I18N = True

USE_TZ = True


# ==============================================================================
# CONFIGURACIÓN DE ARCHIVOS ESTÁTICOS Y MEDIA
# ==============================================================================

# URL y directorio de archivos estáticos
STATIC_URL = '/static/'
# Directorios donde Django buscará archivos estáticos
STATICFILES_DIRS = [
    BASE_DIR / 'static', 
]

# Directorio donde se recogerán todos los estáticos para producción (ejecutar collectstatic)
STATIC_ROOT = '/home/patarroyoalexis/inventario_tecnologico/staticfiles'

# URL y directorio de archivos subidos por el usuario (MEDIA)
MEDIA_URL = '/media/'
# Directorio físico donde se guardarán los archivos subidos (inventario_tecnologico/media/)
MEDIA_ROOT = os.path.join(BASE_DIR, 'media') 


# ==============================================================================
# CONFIGURACIÓN MISCELÁNEA
# ==============================================================================

# Tipo de campo para la clave primaria automática
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==============================================================================
# CONFIGURACIÓN DE LOGGING
# ==============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'maxBytes': 1024 * 1024 * 5, # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}

AUTHENTICATION_BACKENDS = [
    'usuarios.backends.AprobacionRequeridaBackend',  # Tu backend personalizado
    'django.contrib.auth.backends.ModelBackend',     # Backend por defecto (fallback)
]
