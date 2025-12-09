# usuarios/views.py
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth import authenticate, login

from .forms import UsuarioCreationForm, UsuarioChangeForm
from .models import Usuario

# ==============================================================================
# 1. Vistas de Autenticación
# ==============================================================================

class UsuarioLoginView(LoginView):
    """
    Vista de inicio de sesión personalizada.
    Utiliza el template 'usuarios/login.html'.
    """
    template_name = 'usuarios/login.html'
    
    def form_valid(self, form):
        """Verifica que el usuario esté aprobado antes de permitir el login."""
        user = form.get_user()
        
        # Verifica si el usuario está aprobado
        if not user.is_approved:
            messages.error(
                self.request,
                'Tu cuenta está pendiente de aprobación por un administrador. '
                'Por favor, espera a que tu cuenta sea activada.'
            )
            return redirect('usuarios:login')
        
        # Si está aprobado, procede con el login normal
        return super().form_valid(form)


class UsuarioLogoutView(LogoutView):
    """
    Vista de cierre de sesión.
    El LOGOUT_REDIRECT_URL se define en settings.py
    """
    next_page = reverse_lazy('usuarios:login') # Redirigir al login después de cerrar sesión


class UsuarioRegistroView(CreateView):
    """
    Vista para el registro de nuevos usuarios.
    Utiliza el template 'usuarios/registro.html'.
    """
    model = Usuario
    form_class = UsuarioCreationForm
    template_name = 'usuarios/registro.html'
    success_url = reverse_lazy('usuarios:login') # Redirigir al login tras el registro

    def form_valid(self, form):
        """Añade un mensaje de éxito tras un registro válido."""
        response = super().form_valid(form)
        messages.success(
            self.request, 
            '¡Cuenta creada con éxito! Tu registro está pendiente de aprobación por un administrador. '
            'Te notificaremos cuando puedas iniciar sesión.'
        )
        return response


# ==============================================================================
# 2. Vistas de Perfil y Gestión
# ==============================================================================

class PerfilUsuarioView(LoginRequiredMixin, UpdateView):
    """
    Vista para que el usuario edite su propia información de perfil.
    Utiliza el template 'usuarios/perfil.html'.
    """
    model = Usuario
    form_class = UsuarioChangeForm
    template_name = 'usuarios/perfil.html'
    
    # Redirige a la misma página de perfil tras la actualización
    def get_success_url(self):
        return reverse_lazy('usuarios:perfil', kwargs={'pk': self.request.user.pk})

    def get_object(self):
        """Asegura que solo se pueda editar el perfil del usuario logueado."""
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Tu perfil ha sido actualizado.')
        return response


class GestionarAccesosView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Vista para que un Superusuario o Staff gestione los permisos de otros usuarios.
    Utiliza el template 'usuarios/gestionar_accesos.html'.
    """
    model = Usuario
    form_class = UsuarioChangeForm # O un formulario más simple si es solo para permisos
    template_name = 'usuarios/gestionar_accesos.html'
    
    # Se utiliza el mismo formulario de cambio, pero se puede crear uno específico
    fields = ('is_active', 'is_staff', 'is_superuser', 'is_approved', 'groups')
    
    # Redirige a una lista de usuarios (que necesitaríamos crear, por ahora a home)
    success_url = reverse_lazy('inventario:dashboard') 

    def test_func(self):
        """Solo permite el acceso a usuarios con permiso de staff."""
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Permisos del usuario {self.object.email} actualizados.')
        return response