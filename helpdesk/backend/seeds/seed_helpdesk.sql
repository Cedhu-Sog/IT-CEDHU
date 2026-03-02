INSERT INTO tickets (
    ticket_numero, solicitante_nombre, ubicacion, descripcion, estado,
    fecha_hora_registro, fecha_hora_cierre, zona_horaria_cliente,
    prioridad, categoria, canal, activo_inventario_id,
    tiempo_cierre_seg, tiempo_en_pendiente_seg
) VALUES
('HD-20260115-0001', 'Ana Ruiz', 'Sede Norte - Aula 2', 'No enciende proyector', 'CERRADO', NOW() - INTERVAL '3 days', NOW() - INTERVAL '2 days 23 hours', 'America/Bogota', 'MEDIA', 'hardware', 'presencial', 'INV-001', 3600, 1200),
('HD-20260115-0002', 'Carlos Pérez', 'Sede Centro - Oficina TI', 'Error de acceso al correo institucional', 'PENDIENTE', NOW() - INTERVAL '5 hours', NULL, 'America/Bogota', 'ALTA', 'cuentas', 'correo', NULL, NULL, 1800),
('HD-20260115-0003', 'Laura Gómez', 'Sede Sur - Biblioteca', 'Intermitencia de red WiFi', 'ABIERTO', NOW() - INTERVAL '2 hours', NULL, 'America/Bogota', 'ALTA', 'red', 'whatsapp', NULL, NULL, 0);

INSERT INTO ticket_eventos (ticket_id, estado_anterior, estado_nuevo, fecha_hora_cambio, usuario_que_cambia, nota_del_cambio)
SELECT id, 'ABIERTO', estado, NOW() - INTERVAL '1 hour', 'system', 'Carga inicial de seed'
FROM tickets
WHERE estado <> 'ABIERTO';
