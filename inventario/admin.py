# inventario/admin.py
from django.contrib import admin
from .models import TipoDispositivo, EstadoElemento, Elemento

# =============================
#   TITULOS PERSONALIZADOS DJANGO ADMIN
# =============================

admin.site.site_header = "Panel de Administración Inventario IT-CEDHU"
admin.site.site_title = "Panel IT-CEDHU"
admin.site.index_title = "Gestión Administrativa"

# ==============================================================================
# 1. Administración del Modelo Elemento (Principal)
# ==============================================================================

class ElementoAdmin(admin.ModelAdmin):
    """
    Configuración de la visualización del modelo Elemento en el panel de administración.
    """
    # Campos que se muestran en la lista
    list_display = (
        'serial', 
        'nombre_completo', # Método personalizado
        'tipo_dispositivo', 
        'marca', 
        'localizacion', 
        'estado', 
        'usuario_registro',
        'fecha_adquisicion',
    )
    
    # Campos que permiten hacer clic para ir a la página de edición
    list_display_links = ('serial', 'nombre_completo')
    
    # Filtros laterales
    list_filter = ('estado', 'tipo_dispositivo', 'marca', 'localizacion', 'fecha_adquisicion')
    
    # Campos de búsqueda
    search_fields = ('serial', 'marca', 'modelo', 'descripcion', 'localizacion')
    
    # Ordenamiento por defecto
    ordering = ('estado', 'localizacion', 'serial')

    # Grupos de campos para la página de edición del elemento
    fieldsets = (
        ('INFORMACIÓN CLAVE', {
            'fields': (('tipo_dispositivo', 'marca', 'modelo'), 'serial', 'descripcion', ('precio', 'fecha_adquisicion'))
        }),
        ('UBICACIÓN Y ESTADO', {
            'fields': (('localizacion', 'estado'), 'imagen')
        }),
        ('AUDITORÍA', {
            'fields': ('usuario_registro', 'fecha_registro', 'fecha_actualizacion'),
            'classes': ('collapse',), # Oculta este grupo por defecto
        }),
    )

    # Campos de solo lectura
    readonly_fields = ('usuario_registro', 'fecha_registro', 'fecha_actualizacion')
    
    def save_model(self, request, obj, form, change):
        """Sobrescribe el método save_model para asignar el usuario que registra/modifica."""
        # Solo asigna el usuario de registro si el objeto es nuevo (no 'change')
        if not change:
            obj.usuario_registro = request.user
        super().save_model(request, obj, form, change)

    def nombre_completo(self, obj):
        """Método helper para mostrar Marca y Modelo en la lista."""
        return f"{obj.marca} {obj.modelo}"
    nombre_completo.short_description = 'Marca y Modelo'


# ==============================================================================
# 2. Registros de Catálogos (Modelos simples)
# ==============================================================================

# Registra los modelos con sus configuraciones por defecto (solo se añade la búsqueda)
admin.site.register(TipoDispositivo, admin.ModelAdmin)
admin.site.register(EstadoElemento, admin.ModelAdmin)

# Registra el modelo principal con su clase de administración personalizada
admin.site.register(Elemento, ElementoAdmin)