# inventario/filters.py
import django_filters
# Importar forms para usar los Widgets estándar de Django
from django import forms # <-- Nueva importación
from django.db import models # <-- Ya estaba importado, pero lo mantenemos
from .models import Elemento, TipoDispositivo, EstadoElemento

class ElementoFilter(django_filters.FilterSet):
    """
    Clase de filtro para el modelo Elemento.
    """
    
    # Campo de búsqueda global (por texto) que busca en múltiples campos de Elemento
    q = django_filters.CharFilter(
        method='filter_global_search', 
        label='Buscar (Serial, Marca, Modelo, Ubicación)',
        # Usar el TextInput de django.forms en lugar de django_filters.widgets.TextInput
        widget=forms.TextInput(attrs={'placeholder': 'Serial, Marca, Modelo o Ubicación'}) 
    )
    
    # Filtro por rango de fechas de adquisición
    fecha_desde = django_filters.DateFilter(
        field_name='fecha_adquisicion', 
        lookup_expr='gte', 
        label='Adquirido Desde',
        # Usar el DateInput de django.forms
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    fecha_hasta = django_filters.DateFilter(
        field_name='fecha_adquisicion', 
        lookup_expr='lte', 
        label='Adquirido Hasta',
        # Usar el DateInput de django.forms
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = Elemento
        fields = [
            'tipo_dispositivo', 
            'estado', 
            'marca', 
            'localizacion',
        ]
        
    def filter_global_search(self, queryset, name, value):
        """
        Método de filtrado personalizado para realizar una búsqueda global.
        """
        if not value:
            return queryset
        
        return queryset.filter(
            models.Q(serial__icontains=value) |
            models.Q(marca__icontains=value) |
            models.Q(modelo__icontains=value) |
            models.Q(localizacion__icontains=value)
        ).distinct()