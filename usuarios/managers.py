# usuarios/managers.py
from django.contrib.auth.base_user import BaseUserManager

class UsuarioManager(BaseUserManager):
    """
    Manager de modelo de usuario personalizado.
    Define cómo se crean los usuarios (create_user) y superusuarios (create_superuser),
    utilizando el email como identificador único en lugar del nombre de usuario.
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Crea y guarda un Usuario con el email y la contraseña dados.
        """
        if not email:
            raise ValueError('El email debe ser proporcionado.')
        
        # Normaliza el email a minúsculas
        email = self.normalize_email(email)
        
        # Si el usuario es staff o superuser, se aprueba automáticamente
        if extra_fields.get('is_staff') or extra_fields.get('is_superuser'):
            extra_fields.setdefault('is_approved', True)
        
        # Crea la instancia del modelo de usuario
        user = self.model(email=email, **extra_fields)
        
        # Asigna la contraseña hasheada
        user.set_password(password)
        
        # Guarda el usuario en la base de datos
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Crea y guarda un Superusuario, el cual tiene todos los permisos.
        """
        # Asegura que las banderas de superusuario, staff y aprobación estén en True
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_approved', True)  # NUEVO: Aprobación automática

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superusuario debe tener is_superuser=True.')
        if extra_fields.get('is_approved') is not True:
            raise ValueError('Superusuario debe tener is_approved=True.')

        # Llama a create_user con los campos de superusuario
        return self.create_user(email, password, **extra_fields)