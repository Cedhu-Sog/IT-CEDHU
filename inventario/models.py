# inventario/models.py
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from .utils import limpiar_nombre_archivo

# ==============================================================================
# 1. Modelos de Catálogo (Foreign Keys)
# ==============================================================================

class TipoDispositivo(models.Model):
    """Define si es una Laptop, Monitor, Impresora, Servidor, etc."""
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Tipo de Dispositivo")
    
    class Meta:
        verbose_name = 'Tipo de Dispositivo'
        verbose_name_plural = 'Tipos de Dispositivos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class EstadoElemento(models.Model):
    """Define si está 'Activo', 'En Reparación', 'Baja', 'Almacén', etc."""
    nombre = models.CharField(max_length=50, unique=True, verbose_name="Estado")
    descripcion = models.TextField(blank=True, verbose_name="Descripción del Estado")
    
    class Meta:
        verbose_name = 'Estado del Elemento'
        verbose_name_plural = 'Estados de Elementos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

# ==============================================================================
# 2. Modelo Principal del Inventario
# ==============================================================================

class Elemento(models.Model):
    """Representa un único ítem en el inventario tecnológico."""
    
    # 🔢 Control de Cantidad vs Serial
    maneja_cantidad = models.BooleanField(
        default=False,
        verbose_name="¿Maneja Cantidad?",
        help_text="Marcar si este elemento se controla por cantidad (ej: cables, mouse) en lugar de serial único."
    )
    
    cantidad = models.PositiveIntegerField(
        default=1,
        verbose_name="Cantidad",
        help_text="Cantidad de unidades disponibles (solo si no tiene serial único)."
    )
    
    # 📝 Identificación
    tipo_dispositivo = models.ForeignKey(
        TipoDispositivo, 
        on_delete=models.PROTECT, 
        verbose_name="Tipo de Dispositivo"
    )
    marca = models.CharField(max_length=100, verbose_name="Marca")
    modelo = models.CharField(max_length=100, verbose_name="Modelo")
    serial = models.CharField(
        max_length=150, 
        unique=True, 
        blank=True,  # Ahora puede estar vacío
        null=True,   # Ahora puede ser NULL
        verbose_name="Número de Serie / Etiqueta de Activo",
        help_text="Identificador único del equipo (opcional si maneja cantidad)."
    )
    
    # 📍 Localización y Estado
    localizacion = models.CharField(max_length=150, verbose_name="Localización / Ubicación Física")
    estado = models.ForeignKey(
        EstadoElemento, 
        on_delete=models.PROTECT, 
        default=1, 
        verbose_name="Estado Actual"
    )

    # 💰 Información Adicional
    descripcion = models.TextField(blank=True, verbose_name="Especificaciones / Notas")
    fecha_adquisicion = models.DateField(verbose_name="Fecha de Adquisición")
    precio = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name="Costo Adquisición"
    )
    
    # 🖼️ Multimedia
    imagen = models.ImageField(
        upload_to=limpiar_nombre_archivo, 
        blank=True, 
        null=True, 
        verbose_name="Foto del Elemento"
    )
    
    # 👤 Auditoría
    usuario_registro = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name="Registrado Por"
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Elemento de Inventario'
        verbose_name_plural = 'Elementos de Inventario'
        ordering = ['tipo_dispositivo', 'marca', 'modelo']

    def clean(self):
        """Validación personalizada para asegurar integridad de datos"""
        super().clean()
        
        # Si NO maneja cantidad, DEBE tener serial
        if not self.maneja_cantidad and not self.serial:
            raise ValidationError({
                'serial': 'Los elementos que no manejan cantidad deben tener un número de serie único.'
            })
        
        # Si maneja cantidad, NO debe tener serial
        if self.maneja_cantidad and self.serial:
            raise ValidationError({
                'serial': 'Los elementos que manejan cantidad no deben tener número de serie.',
                'maneja_cantidad': 'Desmarque esta opción si desea asignar un serial único.'
            })
        
        # Si maneja cantidad, debe tener al menos 1 unidad
        if self.maneja_cantidad and self.cantidad < 1:
            raise ValidationError({
                'cantidad': 'La cantidad debe ser al menos 1.'
            })

    def save(self, *args, **kwargs):
        # Si maneja cantidad, limpiar el serial
        if self.maneja_cantidad:
            self.serial = None
        
        # Si no maneja cantidad, establecer cantidad en 1
        if not self.maneja_cantidad:
            self.cantidad = 1
            
        self.full_clean()  # Ejecutar validaciones
        super().save(*args, **kwargs)

    def __str__(self):
        if self.maneja_cantidad:
            return f"[{self.cantidad} uds.] {self.tipo_dispositivo} - {self.marca} {self.modelo}"
        else:
            return f"[{self.serial}] {self.tipo_dispositivo} - {self.marca} {self.modelo}"