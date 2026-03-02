CREATE TYPE ticket_status AS ENUM ('ABIERTO','PENDIENTE','CERRADO');
CREATE TYPE ticket_priority AS ENUM ('BAJA','MEDIA','ALTA');
CREATE TYPE ticket_category AS ENUM ('hardware','software','red','cuentas','otros');
CREATE TYPE ticket_channel AS ENUM ('presencial','correo','whatsapp','telefono','otro');

CREATE TABLE tickets (
    id BIGSERIAL PRIMARY KEY,
    ticket_numero VARCHAR(32) NOT NULL UNIQUE,
    solicitante_nombre TEXT NOT NULL,
    ubicacion TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    estado ticket_status NOT NULL DEFAULT 'ABIERTO',
    fecha_hora_registro TIMESTAMPTZ NOT NULL,
    fecha_hora_cierre TIMESTAMPTZ NULL,
    zona_horaria_cliente VARCHAR(64) NOT NULL DEFAULT 'UTC',
    prioridad ticket_priority NULL,
    categoria ticket_category NULL,
    canal ticket_channel NULL,
    activo_inventario_id VARCHAR(128) NULL,
    primera_respuesta_at TIMESTAMPTZ NULL,
    tiempo_primera_respuesta_seg INT NULL,
    tiempo_cierre_seg INT NULL,
    tiempo_en_pendiente_seg INT NOT NULL DEFAULT 0,
    pendiente_inicio_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_tickets_tiempo_pendiente_nonnegative CHECK (tiempo_en_pendiente_seg >= 0)
);

CREATE INDEX idx_tickets_estado ON tickets (estado);
CREATE INDEX idx_tickets_fecha_hora_registro ON tickets (fecha_hora_registro);
CREATE INDEX idx_tickets_ubicacion ON tickets (ubicacion);

CREATE TABLE ticket_eventos (
    id BIGSERIAL PRIMARY KEY,
    ticket_id BIGINT NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    estado_anterior ticket_status NOT NULL,
    estado_nuevo ticket_status NOT NULL,
    fecha_hora_cambio TIMESTAMPTZ NOT NULL,
    usuario_que_cambia VARCHAR(128) NOT NULL DEFAULT 'system',
    nota_del_cambio TEXT NULL
);

CREATE INDEX idx_ticket_eventos_ticket_id ON ticket_eventos (ticket_id);
CREATE INDEX idx_ticket_eventos_fecha_hora_cambio ON ticket_eventos (fecha_hora_cambio);
