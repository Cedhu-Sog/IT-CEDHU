# usuarios/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views # Usaremos algunas vistas de auth por si acaso, aunque ya definimos las nuestras
from . import views

# Define el namespace (espacio de nombres) para esta app. 
# Esto ayuda a evitar conflictos con nombres de URL en otras apps.
app_name = 'usuarios' 

urlpatterns = [
    # Autenticación
    # Usamos nuestras vistas basadas en clases para login y logout
    path('login/', views.UsuarioLoginView.as_view(), name='login'),
    path('logout/', views.UsuarioLogoutView.as_view(), name='logout'),
    path('registro/', views.UsuarioRegistroView.as_view(), name='registro'),
    
    # Gestión de Perfil
    # Se utiliza el PK (Primary Key) del usuario en la URL para identificar el perfil a editar
    path('perfil/<int:pk>/', views.PerfilUsuarioView.as_view(), name='perfil'),
    
    # Gestión de Accesos (solo para Staff/Superusuarios)
    # También requiere el PK del usuario a quien se le gestionarán los permisos
    path('gestionar-accesos/<int:pk>/', views.GestionarAccesosView.as_view(), name='gestionar_accesos'),

    # Rutas para recuperación de contraseña (usando las vistas de Django por defecto)
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='usuarios/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='usuarios/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='usuarios/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='usuarios/password_reset_complete.html'), name='password_reset_complete'),
]