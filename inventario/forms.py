# inventario/forms.py
from django import forms
from .models import Elemento

class ElementoForm(forms.ModelForm):
    """
    Formulario para la creación y edición de elementos del inventario.
    Ahora soporta elementos con serial único o por cantidad.
    """
    class Meta:
        model = Elemento
        fields = [
            'maneja_cantidad',  # Nuevo campo
            'cantidad',         # Nuevo campo
            'tipo_dispositivo',
            'marca',
            'modelo',
            'serial',
            'localizacion',
            'estado',
            'descripcion',
            'fecha_adquisicion',
            'precio',
            'imagen',
        ]
        
        widgets = {
            'fecha_adquisicion': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control'
            }),
            'descripcion': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Especificaciones técnicas o notas adicionales',
                'class': 'form-control'
            }),
            'serial': forms.TextInput(attrs={
                'placeholder': 'Ej. S/N: XYZ12345',
                'class': 'form-control'
            }),
            'maneja_cantidad': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'id_maneja_cantidad'
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'id': 'id_cantidad'
            }),
            'tipo_dispositivo': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'localizacion': forms.TextInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hacer que serial no sea requerido por defecto
        self.fields['serial'].required = False
        
        # Agregar clases CSS y atributos para JavaScript
        self.fields['serial'].widget.attrs.update({
            'data-field': 'serial-field'
        })
        self.fields['cantidad'].widget.attrs.update({
            'data-field': 'cantidad-field'
        })
        
    def clean(self):
        cleaned_data = super().clean()
        maneja_cantidad = cleaned_data.get('maneja_cantidad')
        serial = cleaned_data.get('serial')
        cantidad = cleaned_data.get('cantidad')
        
        # Validar que si NO maneja cantidad, debe tener serial
        if not maneja_cantidad and not serial:
            self.add_error('serial', 'Debe ingresar un número de serie para elementos individuales.')
        
        # Validar que si maneja cantidad, NO debe tener serial
        if maneja_cantidad and serial:
            self.add_error('serial', 'Los elementos por cantidad no deben tener número de serie.')
        
        # Validar cantidad mínima
        if maneja_cantidad and (not cantidad or cantidad < 1):
            self.add_error('cantidad', 'Debe ingresar una cantidad válida (mínimo 1).')
        
        return cleaned_data
    
    def clean_serial(self):
        """
        Validación personalizada para el número de serie.
        """
        serial = self.cleaned_data.get('serial')
        if serial:
            return serial.upper().strip()
        return serial