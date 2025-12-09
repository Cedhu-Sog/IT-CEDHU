from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.http import urlencode

from .forms import UsuarioCreationForm, UsuarioChangeForm
from .models import Usuario

class UsuarioAdmin(BaseUserAdmin):
    """
    Clase de administración para el modelo Usuario personalizado.
    """
    form = UsuarioChangeForm 
    add_form = UsuarioCreationForm

    # AGREGADO: is_approved en la lista de display
    list_display = ('email', 'nombre', 'apellido', 'estado_aprobacion', 'is_staff', 'is_active', 'date_joined')
    
    # AGREGADO: Filtro por estado de aprobación
    list_filter = ('is_approved', 'is_staff', 'is_superuser', 'is_active', 'date_joined')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información Personal', {'fields': ('nombre', 'apellido')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_approved', 'groups', 'user_permissions')}),
        ('Fechas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nombre', 'apellido', 'password1', 'password2'),
        }),
    )
    
    search_fields = ('email', 'nombre', 'apellido')
    ordering = ('email',)
    readonly_fields = ('last_login', 'date_joined')

    # NUEVO: Acciones personalizadas para aprobar/rechazar usuarios
    actions = ['aprobar_usuarios', 'rechazar_usuarios']

    def estado_aprobacion(self, obj):
        """Muestra el estado de aprobación con colores."""
        if obj.is_approved:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Aprobado</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Pendiente</span>'
            )
    estado_aprobacion.short_description = 'Estado de Aprobación'

    def aprobar_usuarios(self, request, queryset):
        """Aprueba los usuarios seleccionados."""
        updated = queryset.update(is_approved=True, is_active=True)
        self.message_user(
            request,
            f'{updated} usuario(s) han sido aprobados correctamente.'
        )
    aprobar_usuarios.short_description = "✓ Aprobar usuarios seleccionados"

    def rechazar_usuarios(self, request, queryset):
        """Rechaza los usuarios seleccionados (los desactiva y marca como no aprobados)."""
        updated = queryset.update(is_approved=False, is_active=False)
        self.message_user(
            request,
            f'{updated} usuario(s) han sido rechazados y desactivados.',
            level='warning'
        )
    rechazar_usuarios.short_description = "✗ Rechazar usuarios seleccionados"

    def get_queryset(self, request):
        """Personaliza el queryset para mostrar usuarios pendientes primero."""
        qs = super().get_queryset(request)
        # Ordena usuarios no aprobados primero
        return qs.order_by('is_approved', '-date_joined')

admin.site.register(Usuario, UsuarioAdmin)