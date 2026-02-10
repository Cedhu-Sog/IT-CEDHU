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
            'maneja_cantidad',
            'cantidad',
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
        
        # Hacer que serial no sea requerido por defecto (se valida en clean())
        self.fields['serial'].required = False
        self.fields['cantidad'].required = False
        
        # Agregar atributos para JavaScript
        self.fields['serial'].widget.attrs.update({
            'data-field': 'serial-field'
        })
        self.fields['cantidad'].widget.attrs.update({
            'data-field': 'cantidad-field'
        })
        
    def clean(self):
        cleaned_data = super().clean()
        maneja_cantidad = cleaned_data.get('maneja_cantidad', False)
        serial = cleaned_data.get('serial', '').strip() if cleaned_data.get('serial') else ''
        cantidad = cleaned_data.get('cantidad')
        
        # CASO 1: Elemento con SERIAL ÚNICO (maneja_cantidad = False)
        if not maneja_cantidad:
            # Debe tener serial
            if not serial:
                self.add_error('serial', 'Debe ingresar un número de serie para elementos individuales.')
            # Limpiar cantidad (se establecerá en 1 automáticamente en el modelo)
            cleaned_data['cantidad'] = 1
        
        # CASO 2: Elemento por CANTIDAD (maneja_cantidad = True)
        else:
            # NO debe tener serial
            if serial:
                self.add_error('serial', 'Los elementos por cantidad no deben tener número de serie. Deje este campo vacío.')
            # Limpiar serial
            cleaned_data['serial'] = None
            
            # Debe tener cantidad válida
            if not cantidad or cantidad < 1:
                self.add_error('cantidad', 'Debe ingresar una cantidad válida (mínimo 1).')
        
        return cleaned_data
    
    def clean_serial(self):
        """
        Validación y normalización del número de serie.
        """
        serial = self.cleaned_data.get('serial')
        if serial:
            serial = serial.upper().strip()
            # Solo retornar si tiene contenido real
            return serial if serial else None
        return None