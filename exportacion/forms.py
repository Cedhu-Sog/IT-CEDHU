# exportacion/forms.py
from django import forms

class CargarBDForm(forms.Form):
    """
    Formulario simple para subir el archivo de base de datos (.sqlite3).
    """
    archivo_bd = forms.FileField(
        label='Seleccionar Archivo de Respaldo (.sqlite3)',
        help_text='Sube el archivo de la base de datos de respaldo (db.sqlite3).',
        # El atributo accept ayuda al navegador a filtrar, pero no es una validación de seguridad
        widget=forms.FileInput(attrs={'accept': '.sqlite3, .db'}) 
    )

    def clean_archivo_bd(self):
        """Asegura que el archivo subido tenga una extensión de base de datos SQLite."""
        archivo = self.cleaned_data.get('archivo_bd')
        if archivo:
            # Simple verificación de extensión
            extension = archivo.name.split('.')[-1].lower()
            if extension not in ['sqlite3', 'db']:
                raise forms.ValidationError("El archivo debe ser un respaldo de base de datos con extensión .sqlite3 o .db")
        return archivo