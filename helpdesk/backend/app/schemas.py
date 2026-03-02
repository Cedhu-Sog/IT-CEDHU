from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .models import TicketCategory, TicketChannel, TicketPriority, TicketStatus


class TicketCreate(BaseModel):
    solicitante_nombre: str = Field(min_length=1)
    ubicacion: str = Field(min_length=1)
    descripcion: str = Field(min_length=1)
    zona_horaria_cliente: str = Field(default="UTC")
    prioridad: TicketPriority | None = None
    categoria: TicketCategory | None = None
    canal: TicketChannel | None = None
    activo_inventario_id: str | None = None


class TicketEstadoPatch(BaseModel):
    estado_nuevo: TicketStatus
    usuario_que_cambia: str = "system"
    nota_del_cambio: str | None = None


class TicketEventoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    estado_anterior: TicketStatus
    estado_nuevo: TicketStatus
    fecha_hora_cambio: datetime
    usuario_que_cambia: str
    nota_del_cambio: str | None


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_numero: str
    solicitante_nombre: str
    ubicacion: str
    descripcion: str
    estado: TicketStatus
    fecha_hora_registro: datetime
    fecha_hora_cierre: datetime | None
    zona_horaria_cliente: str
    prioridad: TicketPriority | None
    categoria: TicketCategory | None
    canal: TicketChannel | None
    activo_inventario_id: str | None
    tiempo_primera_respuesta_seg: int | None
    tiempo_cierre_seg: int | None
    tiempo_en_pendiente_seg: int


class TicketDetalleOut(TicketOut):
    eventos: list[TicketEventoOut]


class KpiResumen(BaseModel):
    tickets_abiertos: int
    tickets_pendientes: int
    tickets_cerrados: int
    tiempo_promedio_cierre_seg: float | None
    top_ubicaciones: list[dict]
