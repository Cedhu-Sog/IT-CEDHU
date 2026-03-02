import enum
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class TicketStatus(str, enum.Enum):
    ABIERTO = "ABIERTO"
    PENDIENTE = "PENDIENTE"
    CERRADO = "CERRADO"


class TicketPriority(str, enum.Enum):
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"


class TicketCategory(str, enum.Enum):
    HARDWARE = "hardware"
    SOFTWARE = "software"
    RED = "red"
    CUENTAS = "cuentas"
    OTROS = "otros"


class TicketChannel(str, enum.Enum):
    PRESENCIAL = "presencial"
    CORREO = "correo"
    WHATSAPP = "whatsapp"
    TELEFONO = "telefono"
    OTRO = "otro"


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticket_numero: Mapped[str] = mapped_column(String(32), nullable=False, unique=True, index=True)
    solicitante_nombre: Mapped[str] = mapped_column(Text, nullable=False)
    ubicacion: Mapped[str] = mapped_column(Text, nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    estado: Mapped[TicketStatus] = mapped_column(Enum(TicketStatus, name="ticket_status"), nullable=False)
    fecha_hora_registro: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fecha_hora_cierre: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    zona_horaria_cliente: Mapped[str] = mapped_column(String(64), nullable=False, default="UTC")

    prioridad: Mapped[TicketPriority | None] = mapped_column(Enum(TicketPriority, name="ticket_priority"), nullable=True)
    categoria: Mapped[TicketCategory | None] = mapped_column(Enum(TicketCategory, name="ticket_category"), nullable=True)
    canal: Mapped[TicketChannel | None] = mapped_column(Enum(TicketChannel, name="ticket_channel"), nullable=True)
    activo_inventario_id: Mapped[str | None] = mapped_column(String(128), nullable=True)

    primera_respuesta_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    tiempo_primera_respuesta_seg: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tiempo_cierre_seg: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tiempo_en_pendiente_seg: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pendiente_inicio_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    eventos: Mapped[list["TicketEvento"]] = relationship("TicketEvento", back_populates="ticket", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("tiempo_en_pendiente_seg >= 0", name="ck_tickets_tiempo_pendiente_nonnegative"),
    )


class TicketEvento(Base):
    __tablename__ = "ticket_eventos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    estado_anterior: Mapped[TicketStatus] = mapped_column(Enum(TicketStatus, name="ticket_status"), nullable=False)
    estado_nuevo: Mapped[TicketStatus] = mapped_column(Enum(TicketStatus, name="ticket_status"), nullable=False)
    fecha_hora_cambio: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    usuario_que_cambia: Mapped[str] = mapped_column(String(128), nullable=False, default="system")
    nota_del_cambio: Mapped[str | None] = mapped_column(Text, nullable=True)

    ticket: Mapped[Ticket] = relationship("Ticket", back_populates="eventos")
