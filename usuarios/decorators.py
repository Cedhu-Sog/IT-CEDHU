# usuarios/decorators.py
from django.shortcuts import redirect
from django.conf import settings
from functools import wraps
from django.contrib import messages

# ==============================================================================
# 1. Decorador para Usuarios NO Autenticados
# ==============================================================================

def usuario_no_autenticado(view_func):
    """
    Redirige a un usuario a la página de inicio (LOGIN_REDIRECT_URL) si ya está autenticado.
    Útil para restringir el acceso a vistas como 'login' y 'registro'.
    """
    @wraps(view_func)
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            # Redirige a la URL definida en settings.py (por defecto '/')
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            # Si no está autenticado, permite el acceso a la vista
            return view_func(request, *args, **kwargs)
    return wrapper_func


# ==============================================================================
# 2. Decorador para Usuarios Staff/Admin
# ==============================================================================

def staff_required(view_func):
    """
    Restringe el acceso a la vista solo a usuarios que son staff (is_staff=True) o superusuarios.
    Muestra un mensaje de error y redirige a la página de inicio de sesión o a una página de error 403.
    """
    @wraps(view_func)
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "No tienes permisos suficientes para acceder a esta página.")
            # Podrías redirigir a una página de error 403 o a la página de inicio
            # Aquí redirigimos al dashboard por simplicidad, pero lo ideal es un error 403.
            return redirect(settings.LOGIN_REDIRECT_URL) 
    return wrapper_func