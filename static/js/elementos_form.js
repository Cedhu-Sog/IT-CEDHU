// static/js/elemento_form.js
// Script para controlar la visibilidad de campos según el tipo de elemento

document.addEventListener('DOMContentLoaded', function() {
    const manejaQuantityCheckbox = document.getElementById('id_maneja_cantidad');
    const serialField = document.getElementById('id_serial');
    const cantidadField = document.getElementById('id_cantidad');
    
    // Obtener los contenedores de los campos (buscar el elemento padre que contiene el label y el input)
    const serialContainer = serialField?.closest('.mb-3') || serialField?.closest('.form-group');
    const cantidadContainer = cantidadField?.closest('.mb-3') || cantidadField?.closest('.form-group');
    
    function toggleFields() {
        const manejaQuantity = manejaQuantityCheckbox?.checked || false;
        
        if (manejaQuantity) {
            // Maneja cantidad: mostrar cantidad, ocultar serial
            if (cantidadContainer) cantidadContainer.style.display = 'block';
            if (serialContainer) serialContainer.style.display = 'none';
            
            // Hacer cantidad requerida y serial opcional
            if (cantidadField) {
                cantidadField.required = true;
                cantidadField.disabled = false;
            }
            if (serialField) {
                serialField.required = false;
                serialField.disabled = true;
                serialField.value = ''; // Limpiar el valor
            }
        } else {
            // Maneja serial: mostrar serial, ocultar cantidad
            if (serialContainer) serialContainer.style.display = 'block';
            if (cantidadContainer) cantidadContainer.style.display = 'none';
            
            // Hacer serial requerido y cantidad opcional
            if (serialField) {
                serialField.required = true;
                serialField.disabled = false;
            }
            if (cantidadField) {
                cantidadField.required = false;
                cantidadField.disabled = true;
                cantidadField.value = '1'; // Valor por defecto
            }
        }
    }
    
    // Ejecutar al cargar la página
    if (manejaQuantityCheckbox) {
        toggleFields();
        
        // Ejecutar cada vez que cambie el checkbox
        manejaQuantityCheckbox.addEventListener('change', toggleFields);
    }
});