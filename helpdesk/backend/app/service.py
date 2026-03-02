from datetime import UTC, datetime

from sqlalchemy import and_, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from .models import Ticket, TicketEvento, TicketStatus
from .schemas import TicketCreate, TicketEstadoPatch


class TicketService:
    def __init__(self, db: Session):
        self.db = db

    def _utc_now(self) -> datetime:
        return datetime.now(UTC)

    def _next_ticket_numero(self, now: datetime) -> str:
        prefix = f"HD-{now.strftime('%Y%m%d')}-"
        like_pattern = f"{prefix}%"
        last_number = self.db.execute(
            select(func.max(Ticket.ticket_numero)).where(Ticket.ticket_numero.like(like_pattern))
        ).scalar_one_or_none()
        seq = 1
        if last_number:
            seq = int(last_number.rsplit("-", 1)[-1]) + 1
        return f"{prefix}{seq:04d}"

    def create_ticket(self, payload: TicketCreate) -> Ticket:
        now = self._utc_now()
        for _ in range(5):
            ticket = Ticket(
                ticket_numero=self._next_ticket_numero(now),
                solicitante_nombre=payload.solicitante_nombre,
                ubicacion=payload.ubicacion,
                descripcion=payload.descripcion,
                estado=TicketStatus.ABIERTO,
                fecha_hora_registro=now,
                zona_horaria_cliente=payload.zona_horaria_cliente,
                prioridad=payload.prioridad,
                categoria=payload.categoria,
                canal=payload.canal,
                activo_inventario_id=payload.activo_inventario_id,
            )
            self.db.add(ticket)
            try:
                self.db.commit()
                self.db.refresh(ticket)
                return ticket
            except IntegrityError:
                self.db.rollback()
                continue
        raise RuntimeError("No se pudo generar ticket_numero único tras múltiples intentos")

    def list_tickets(self, filters: dict) -> list[Ticket]:
        query = select(Ticket).order_by(Ticket.fecha_hora_registro.desc())
        conditions = []
        if filters.get("estado"):
            conditions.append(Ticket.estado == filters["estado"])
        if filters.get("fecha_desde"):
            conditions.append(Ticket.fecha_hora_registro >= filters["fecha_desde"])
        if filters.get("fecha_hasta"):
            conditions.append(Ticket.fecha_hora_registro <= filters["fecha_hasta"])
        if filters.get("ubicacion"):
            conditions.append(Ticket.ubicacion == filters["ubicacion"])
        if filters.get("solicitante"):
            conditions.append(Ticket.solicitante_nombre == filters["solicitante"])
        if conditions:
            query = query.where(and_(*conditions))
        return list(self.db.execute(query).scalars().all())

    def get_ticket(self, ticket_id: int) -> Ticket | None:
        stmt = select(Ticket).where(Ticket.id == ticket_id).options(joinedload(Ticket.eventos))
        return self.db.execute(stmt).unique().scalar_one_or_none()

    def patch_estado(self, ticket_id: int, payload: TicketEstadoPatch) -> Ticket | None:
        ticket = self.get_ticket(ticket_id)
        if not ticket:
            return None

        now = self._utc_now()
        estado_anterior = ticket.estado
        estado_nuevo = payload.estado_nuevo
        if estado_anterior == estado_nuevo:
            return ticket

        if ticket.primera_respuesta_at is None:
            ticket.primera_respuesta_at = now
            ticket.tiempo_primera_respuesta_seg = int((now - ticket.fecha_hora_registro).total_seconds())

        if estado_anterior == TicketStatus.PENDIENTE and ticket.pendiente_inicio_at:
            ticket.tiempo_en_pendiente_seg += int((now - ticket.pendiente_inicio_at).total_seconds())
            ticket.pendiente_inicio_at = None

        if estado_nuevo == TicketStatus.PENDIENTE:
            ticket.pendiente_inicio_at = now
        if estado_nuevo == TicketStatus.CERRADO:
            ticket.fecha_hora_cierre = now
            ticket.tiempo_cierre_seg = int((now - ticket.fecha_hora_registro).total_seconds())

        ticket.estado = estado_nuevo
        evento = TicketEvento(
            ticket_id=ticket.id,
            estado_anterior=estado_anterior,
            estado_nuevo=estado_nuevo,
            fecha_hora_cambio=now,
            usuario_que_cambia=payload.usuario_que_cambia or "system",
            nota_del_cambio=payload.nota_del_cambio,
        )
        self.db.add(evento)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def resumen_kpis(self) -> dict:
        abiertos = self.db.scalar(select(func.count()).select_from(Ticket).where(Ticket.estado == TicketStatus.ABIERTO)) or 0
        pendientes = self.db.scalar(select(func.count()).select_from(Ticket).where(Ticket.estado == TicketStatus.PENDIENTE)) or 0
        cerrados = self.db.scalar(select(func.count()).select_from(Ticket).where(Ticket.estado == TicketStatus.CERRADO)) or 0
        avg_cierre = self.db.scalar(
            select(func.avg(Ticket.tiempo_cierre_seg)).where(Ticket.tiempo_cierre_seg.is_not(None))
        )
        top = self.db.execute(
            select(Ticket.ubicacion, func.count(Ticket.id).label("total"))
            .group_by(Ticket.ubicacion)
            .order_by(func.count(Ticket.id).desc())
            .limit(5)
        ).all()
        return {
            "tickets_abiertos": abiertos,
            "tickets_pendientes": pendientes,
            "tickets_cerrados": cerrados,
            "tiempo_promedio_cierre_seg": float(avg_cierre) if avg_cierre is not None else None,
            "top_ubicaciones": [{"ubicacion": row[0], "total": row[1]} for row in top],
        }
