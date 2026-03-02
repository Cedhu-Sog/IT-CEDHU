from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .inventario_client import InventarioClient
from .models import TicketStatus
from .schemas import KpiResumen, TicketCreate, TicketDetalleOut, TicketEstadoPatch, TicketOut
from .service import TicketService

app = FastAPI(title="Helpdesk API", version="1.0.0")


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.post("/tickets", response_model=TicketOut)
def create_ticket(payload: TicketCreate, db: Session = Depends(get_db)):
    service = TicketService(db)
    return service.create_ticket(payload)


@app.get("/tickets", response_model=list[TicketOut])
def list_tickets(
    estado: TicketStatus | None = None,
    fecha_desde: datetime | None = None,
    fecha_hasta: datetime | None = None,
    ubicacion: str | None = None,
    solicitante: str | None = None,
    db: Session = Depends(get_db),
):
    service = TicketService(db)
    return service.list_tickets(
        {
            "estado": estado,
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta,
            "ubicacion": ubicacion,
            "solicitante": solicitante,
        }
    )


@app.get("/tickets/{ticket_id}", response_model=TicketDetalleOut)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    service = TicketService(db)
    ticket = service.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    return ticket


@app.patch("/tickets/{ticket_id}/estado", response_model=TicketOut)
def patch_ticket_estado(ticket_id: int, payload: TicketEstadoPatch, db: Session = Depends(get_db)):
    service = TicketService(db)
    ticket = service.patch_estado(ticket_id, payload)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    return ticket


@app.get("/kpis/resumen", response_model=KpiResumen)
def kpis_resumen(db: Session = Depends(get_db)):
    service = TicketService(db)
    return service.resumen_kpis()


@app.get("/integraciones/inventario/ubicaciones")
def inventario_ubicaciones(manual_fallback: bool = Query(default=True)):
    data = InventarioClient().obtener_ubicaciones()
    if data:
        return {"modo": "integrado", "items": data}
    if manual_fallback:
        return {"modo": "manual", "items": []}
    raise HTTPException(status_code=502, detail="No se pudo obtener ubicaciones de inventario")


@app.get("/integraciones/inventario/usuarios")
def inventario_usuarios(manual_fallback: bool = Query(default=True)):
    data = InventarioClient().obtener_usuarios()
    if data:
        return {"modo": "integrado", "items": data}
    if manual_fallback:
        return {"modo": "manual", "items": []}
    raise HTTPException(status_code=502, detail="No se pudo obtener usuarios/personas de inventario")
