# Helpdesk App (FastAPI + React)

Aplicación nueva **helpdesk** integrada de forma opcional con la app principal de inventario por API REST.

## 1) Arquitectura propuesta (diagrama textual)

```text
[Frontend React (Vite)]
   |  HTTP/JSON
   v
[Helpdesk API - FastAPI]
   |-- Módulo Tickets (CRUD + cambios de estado)
   |-- Módulo Auditoría (ticket_eventos)
   |-- Módulo KPI (resumen + métricas de duración)
   |-- Módulo Integración Inventario (REST client con fallback manual)
   v
[PostgreSQL]
   |-- tickets
   |-- ticket_eventos

[App Inventario existente]
   ^
   | GET /inventario/ubicaciones
   | GET /inventario/usuarios o /inventario/personas
   |
(opcional, con token/API key; si falla => modo manual)
```

## 2) Modelo de datos y migraciones

Migración SQL: `backend/migrations/001_create_helpdesk_tables.sql`

- `tickets`
  - PK: `id`
  - `ticket_numero` único
  - estado restringido con ENUM `ABIERTO|PENDIENTE|CERRADO`
  - timestamps UTC (`TIMESTAMPTZ`)
  - campos para analítica: `tiempo_primera_respuesta_seg`, `tiempo_cierre_seg`, `tiempo_en_pendiente_seg`
  - `zona_horaria_cliente` almacenada explícitamente
- `ticket_eventos`
  - auditoría completa de transiciones de estado

## 3) Backend + endpoints

### Requisitos
- Python 3.11+
- PostgreSQL 14+

### Instalación backend

```bash
cd helpdesk/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-helpdesk.txt
```

### Variables de entorno

```bash
export HELPDESK_DATABASE_URL='postgresql+psycopg://postgres:postgres@localhost:5432/helpdesk'
export INVENTARIO_API_BASE_URL='http://localhost:8001'
export INVENTARIO_API_TOKEN='mi_token'
export INVENTARIO_API_TIMEOUT='5'
```

### Levantar API

```bash
uvicorn app.main:app --reload --port 8000
```

### Endpoints implementados
- `POST /tickets`
- `GET /tickets` (filtros: `estado`, `fecha_desde`, `fecha_hasta`, `ubicacion`, `solicitante`)
- `GET /tickets/{id}`
- `PATCH /tickets/{id}/estado`
- `GET /kpis/resumen`
- `GET /integraciones/inventario/ubicaciones`
- `GET /integraciones/inventario/usuarios`

## 4) Frontend mínimo viable

### Instalación y ejecución

```bash
cd helpdesk/frontend
npm install
npm run dev
```

Variables opcionales:

```bash
echo 'VITE_HELPDESK_API_BASE_URL=http://localhost:8000' > .env
```

Incluye:
- Formulario de creación de ticket
- Tabla/lista de tickets con filtro por estado
- Vista detalle con histórico
- Botones de cambio de estado (`PENDIENTE`, `ABIERTO`, `CERRADO`)

## 5) Ejemplos de requests (curl) y datos de prueba

### Ejecutar migración y seed

```bash
psql "$HELPDESK_DATABASE_URL" -f migrations/001_create_helpdesk_tables.sql
psql "$HELPDESK_DATABASE_URL" -f seeds/seed_helpdesk.sql
```

### Crear ticket

```bash
curl -X POST http://localhost:8000/tickets \
  -H 'Content-Type: application/json' \
  -d '{
    "solicitante_nombre":"Juan Torres",
    "ubicacion":"Sede Norte - Sala 1",
    "descripcion":"Impresora sin conexión",
    "zona_horaria_cliente":"America/Bogota",
    "prioridad":"MEDIA",
    "categoria":"hardware",
    "canal":"correo"
  }'
```

### Cambiar a PENDIENTE

```bash
curl -X PATCH http://localhost:8000/tickets/1/estado \
  -H 'Content-Type: application/json' \
  -d '{"estado_nuevo":"PENDIENTE","usuario_que_cambia":"agente.helpdesk","nota_del_cambio":"Esperando repuesto"}'
```

### Cerrar ticket

```bash
curl -X PATCH http://localhost:8000/tickets/1/estado \
  -H 'Content-Type: application/json' \
  -d '{"estado_nuevo":"CERRADO","usuario_que_cambia":"agente.helpdesk","nota_del_cambio":"Resuelto y validado"}'
```

## 6) Consultas SQL y endpoint KPI

### Endpoint

```bash
curl http://localhost:8000/kpis/resumen
```

### SQL útiles para analítica base

Tickets por día:

```sql
SELECT date_trunc('day', fecha_hora_registro) AS dia, count(*) AS total
FROM tickets
GROUP BY 1
ORDER BY 1 DESC;
```

Tickets por semana/mes:

```sql
SELECT date_trunc('week', fecha_hora_registro) AS semana, count(*) AS total
FROM tickets
GROUP BY 1
ORDER BY 1 DESC;

SELECT date_trunc('month', fecha_hora_registro) AS mes, count(*) AS total
FROM tickets
GROUP BY 1
ORDER BY 1 DESC;
```

Duración promedio de cierre por ubicación:

```sql
SELECT ubicacion, AVG(tiempo_cierre_seg) AS promedio_seg
FROM tickets
WHERE tiempo_cierre_seg IS NOT NULL
GROUP BY ubicacion
ORDER BY promedio_seg DESC;
```

Tiempo acumulado en pendiente por ticket:

```sql
SELECT ticket_numero, tiempo_en_pendiente_seg
FROM tickets
ORDER BY tiempo_en_pendiente_seg DESC;
```
