# inventario/views.py
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    TemplateView, ListView, DetailView, 
    CreateView, UpdateView, DeleteView
)
from .filters import ElementoFilter
from .models import Elemento
from .forms import ElementoForm

# ==============================================================================
# 1. Vistas de Inicio y Dashboard
# ==============================================================================

class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Vista principal del sistema (Dashboard).
    """
    template_name = 'dashboard/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Total de elementos (considerando cantidades)
        total_items = 0
        for elemento in Elemento.objects.all():
            if elemento.maneja_cantidad:
                total_items += elemento.cantidad
            else:
                total_items += 1
        
        context['total_elementos'] = total_items
        context['total_registros'] = Elemento.objects.count()
        context['elementos_activos'] = Elemento.objects.filter(estado__nombre__iexact='activo').count()
        context['ultimos_registros'] = Elemento.objects.all().order_by('-fecha_registro')[:5]
        return context


# ==============================================================================
# 2. Vistas CRUD de Elementos de Inventario
# ==============================================================================

class ListaInventarioView(LoginRequiredMixin, ListView):
    """
    Vista para listar todos los elementos del inventario con filtros.
    """
    model = Elemento
    template_name = 'inventario/lista_inventario.html'
    context_object_name = 'elementos'
    paginate_by = 15
    
    def get_queryset(self):
        """Aplicar filtros usando django-filter"""
        queryset = Elemento.objects.all()
        self.filterset = ElementoFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs
    
    def get_context_data(self, **kwargs):
        """Agregar el filterset al contexto para usar en el template"""
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class DetalleElementoView(LoginRequiredMixin, DetailView):
    """
    Vista para ver el detalle de un elemento específico.
    """
    model = Elemento
    template_name = 'inventario/ver_producto.html'
    context_object_name = 'elemento'


class ElementoCreateView(LoginRequiredMixin, CreateView):
    """
    Vista para añadir un nuevo elemento al inventario.
    """
    model = Elemento
    form_class = ElementoForm
    template_name = 'inventario/añadir_elemento.html'
    success_url = reverse_lazy('inventario:lista_inventario')

    def form_valid(self, form):
        form.instance.usuario_registro = self.request.user
        response = super().form_valid(form)
        
        # Mensaje personalizado según el tipo de elemento
        if self.object.maneja_cantidad:
            messages.success(
                self.request, 
                f'Se han añadido {self.object.cantidad} unidades de "{self.object.marca} {self.object.modelo}".'
            )
        else:
            messages.success(
                self.request, 
                f'El elemento con serial "{self.object.serial}" se ha añadido correctamente.'
            )
        return response


class ElementoUpdateView(LoginRequiredMixin, UpdateView):
    """
    Vista para editar un elemento existente.
    """
    model = Elemento
    form_class = ElementoForm
    template_name = 'inventario/editar_elemento.html'
    success_url = reverse_lazy('inventario:lista_inventario')

    def form_valid(self, form):
        response = super().form_valid(form)
        
        if self.object.maneja_cantidad:
            messages.info(
                self.request, 
                f'El elemento "{self.object.marca} {self.object.modelo}" (cantidad: {self.object.cantidad}) ha sido actualizado.'
            )
        else:
            messages.info(
                self.request, 
                f'El elemento con serial "{self.object.serial}" ha sido actualizado.'
            )
        return response


class ElementoDeleteView(LoginRequiredMixin, DeleteView):
    """
    Vista para eliminar un elemento existente.
    """
    model = Elemento
    template_name = 'inventario/confirmar_eliminar.html'
    context_object_name = 'elemento'
    success_url = reverse_lazy('inventario:lista_inventario')

    def form_valid(self, form):
        if self.object.maneja_cantidad:
            element_info = f'{self.object.marca} {self.object.modelo} ({self.object.cantidad} uds.)'
        else:
            element_info = f'Serial: {self.object.serial}'
        
        response = super().form_valid(form)
        messages.error(self.request, f'El elemento "{element_info}" ha sido eliminado permanentemente.')
        return response