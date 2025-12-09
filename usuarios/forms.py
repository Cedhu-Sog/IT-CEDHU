# usuarios/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm 
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import Usuario 

class UsuarioCreationForm(UserCreationForm):
    """
    Formulario personalizado para la creación de un nuevo usuario.
    Aseguramos que los campos 'nombre' y 'apellido' se manejen correctamente.
    """
    # Definimos explícitamente los campos de contraseña
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput,
        help_text="Introduce una contraseña segura."
    )
    password2 = forms.CharField(
        label='Contraseña (confirmación)',
        widget=forms.PasswordInput,
        help_text="Introduce la misma contraseña para verificación."
    )

    class Meta:
        model = Usuario
        fields = ('email', 'nombre', 'apellido')
        
    def clean_password2(self):
        """Verifica que las dos contraseñas coincidan."""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return password2

    def save(self, commit=True):
        """Guarda el usuario con la contraseña hasheada."""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UsuarioChangeForm(UserChangeForm):
    """
    Formulario personalizado para la edición de un usuario existente.
    """
    password = ReadOnlyPasswordHashField(
        label="Contraseña",
        help_text=(
            "Las contraseñas no se almacenan en texto plano, por lo que no hay forma de ver "
            "la contraseña de este usuario, pero puedes cambiarla usando "
            "<a href=\"../password/\">este formulario</a>."
        ),
    )

    class Meta:
        model = Usuario
        fields = ('email', 'nombre', 'apellido', 'password', 'is_active', 'is_staff', 'is_superuser')

    def clean_password(self):
        """Retorna el valor inicial del campo password."""
        return self.initial["password"]