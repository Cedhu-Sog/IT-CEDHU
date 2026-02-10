# exportacion/forms.py
from django import forms

class CargarBDForm(forms.Form):
    """
    Formulario simple para subir el archivo de base de datos PostgreSQL (.sql).
    ACTUALIZADO: Adaptado para PostgreSQL.
    """
    archivo_bd = forms.FileField(
        label='Seleccionar Archivo de Respaldo PostgreSQL (.sql)',
        help_text='Sube el archivo de respaldo de PostgreSQL generado con pg_dump (archivo .sql).',
        # El atributo accept ayuda al navegador a filtrar archivos SQL
        widget=forms.FileInput(attrs={'accept': '.sql'}) 
    )

    def clean_archivo_bd(self):
        """Asegura que el archivo subido tenga una extensión .sql válida para PostgreSQL."""
        archivo = self.cleaned_data.get('archivo_bd')
        if archivo:
            # Verificación de extensión
            extension = archivo.name.split('.')[-1].lower()
            if extension not in ['sql']:
                raise forms.ValidationError("El archivo debe ser un respaldo de PostgreSQL con extensión .sql")
            
            # Verificación adicional: el archivo no debe estar vacío
            if archivo.size == 0:
                raise forms.ValidationError("El archivo de respaldo está vacío.")
                
        return archivo