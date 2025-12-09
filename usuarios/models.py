# usuarios/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

# Importamos el manager que creamos en managers.py para manejar la creación de usuarios
from .managers import UsuarioManager 

class Usuario(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de Usuario personalizado que utiliza el email como nombre de usuario.
    Hereda la funcionalidad de autenticación de AbstractBaseUser y los permisos de PermissionsMixin.
    """
    email = models.EmailField(
        verbose_name='Dirección de correo electrónico',
        max_length=255,
        unique=True,
    )
    nombre = models.CharField(max_length=150, blank=False, verbose_name="Nombre")
    apellido = models.CharField(max_length=150, blank=False, verbose_name="Apellido")
    
    # Campos de estado y permisos requeridos por Django
    is_staff = models.BooleanField(default=False, verbose_name="Es parte del staff")
    is_active = models.BooleanField(default=True, verbose_name="Está activo")
    is_superuser = models.BooleanField(default=False, verbose_name="Es superusuario")
    
    # NUEVO: Campo para controlar la aprobación de usuarios
    is_approved = models.BooleanField(
        default=False, 
        verbose_name="Usuario Aprobado",
        help_text="Indica si el usuario ha sido aprobado por un administrador para acceder al sistema."
    )
    
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    objects = UsuarioManager() # Asigna nuestro Manager personalizado

    USERNAME_FIELD = 'email' # Define el campo que se usa para iniciar sesión
    REQUIRED_FIELDS = [] # No se requieren campos adicionales para la creación

    class Meta:
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'
        
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Retorna el nombre completo del usuario."""
        return f"{self.nombre} {self.apellido}".strip()

    def get_short_name(self):
        """Retorna el nombre corto (nombre de pila)."""
        return self.nombre
    
    def puede_iniciar_sesion(self):
        """Verifica si el usuario puede iniciar sesión (activo Y aprobado)."""
        return self.is_active and self.is_approved