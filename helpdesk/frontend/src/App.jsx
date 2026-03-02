import { useEffect, useState } from 'react'

const API_BASE = import.meta.env.VITE_HELPDESK_API_BASE_URL || 'http://localhost:8000'

async function api(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export default function App() {
  const [tickets, setTickets] = useState([])
  const [selected, setSelected] = useState(null)
  const [filters, setFilters] = useState({ estado: '' })
  const [form, setForm] = useState({
    solicitante_nombre: '',
    ubicacion: '',
    descripcion: '',
    zona_horaria_cliente: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC',
  })

  const loadTickets = async () => {
    const query = new URLSearchParams()
    if (filters.estado) query.set('estado', filters.estado)
    const data = await api(`/tickets?${query.toString()}`)
    setTickets(data)
  }

  const loadDetalle = async (id) => {
    const data = await api(`/tickets/${id}`)
    setSelected(data)
  }

  useEffect(() => {
    loadTickets()
  }, [filters.estado])

  const createTicket = async (e) => {
    e.preventDefault()
    await api('/tickets', { method: 'POST', body: JSON.stringify(form) })
    setForm({ ...form, descripcion: '' })
    await loadTickets()
  }

  const changeEstado = async (id, estado_nuevo) => {
    await api(`/tickets/${id}/estado`, {
      method: 'PATCH',
      body: JSON.stringify({ estado_nuevo, usuario_que_cambia: 'system-ui' }),
    })
    await loadTickets()
    await loadDetalle(id)
  }

  return (
    <div className="container">
      <h1>Helpdesk</h1>
      <section className="card">
        <h2>Crear ticket</h2>
        <form onSubmit={createTicket} className="grid">
          <input placeholder="Solicitante" value={form.solicitante_nombre} onChange={(e) => setForm({ ...form, solicitante_nombre: e.target.value })} required />
          <input placeholder="Ubicación" value={form.ubicacion} onChange={(e) => setForm({ ...form, ubicacion: e.target.value })} required />
          <textarea placeholder="Descripción" value={form.descripcion} onChange={(e) => setForm({ ...form, descripcion: e.target.value })} required />
          <button type="submit">Registrar ticket</button>
        </form>
      </section>

      <section className="card">
        <h2>Tickets</h2>
        <select value={filters.estado} onChange={(e) => setFilters({ ...filters, estado: e.target.value })}>
          <option value="">Todos</option>
          <option value="ABIERTO">ABIERTO</option>
          <option value="PENDIENTE">PENDIENTE</option>
          <option value="CERRADO">CERRADO</option>
        </select>
        <table>
          <thead><tr><th>Número</th><th>Solicitante</th><th>Ubicación</th><th>Estado</th></tr></thead>
          <tbody>
            {tickets.map((t) => (
              <tr key={t.id} onClick={() => loadDetalle(t.id)}>
                <td>{t.ticket_numero}</td><td>{t.solicitante_nombre}</td><td>{t.ubicacion}</td><td>{t.estado}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {selected && (
        <section className="card">
          <h2>Detalle {selected.ticket_numero}</h2>
          <p>{selected.descripcion}</p>
          <div className="actions">
            <button onClick={() => changeEstado(selected.id, 'PENDIENTE')}>Marcar PENDIENTE</button>
            <button onClick={() => changeEstado(selected.id, 'ABIERTO')}>Reabrir ABIERTO</button>
            <button onClick={() => changeEstado(selected.id, 'CERRADO')}>Cerrar</button>
          </div>
          <h3>Histórico</h3>
          <ul>
            {(selected.eventos || []).map((ev) => (
              <li key={ev.id}>{ev.fecha_hora_cambio} | {ev.estado_anterior} → {ev.estado_nuevo} ({ev.usuario_que_cambia})</li>
            ))}
          </ul>
        </section>
      )}
    </div>
  )
}
