from concurrent.futures import ThreadPoolExecutor


def _ticket_payload(suffix: str = ""):
    return {
        "solicitante_nombre": f"Solicitante {suffix}".strip(),
        "ubicacion": "Sede Principal",
        "descripcion": "Equipo no responde",
        "zona_horaria_cliente": "America/Bogota",
    }


def test_creacion_ticket(client):
    response = client.post("/tickets", json=_ticket_payload("A"))
    assert response.status_code == 200
    data = response.json()
    assert data["estado"] == "ABIERTO"
    assert data["ticket_numero"].startswith("HD-")


def test_cambio_a_pendiente(client):
    ticket = client.post("/tickets", json=_ticket_payload("B")).json()
    response = client.patch(
        f"/tickets/{ticket['id']}/estado",
        json={"estado_nuevo": "PENDIENTE", "usuario_que_cambia": "operador"},
    )
    assert response.status_code == 200
    assert response.json()["estado"] == "PENDIENTE"


def test_cambio_a_cerrado_guarda_fecha_cierre(client):
    ticket = client.post("/tickets", json=_ticket_payload("C")).json()
    response = client.patch(
        f"/tickets/{ticket['id']}/estado",
        json={"estado_nuevo": "CERRADO", "usuario_que_cambia": "operador"},
    )
    assert response.status_code == 200
    assert response.json()["fecha_hora_cierre"] is not None


def test_ticket_numero_unico(client):
    def create_one(i: int):
        return client.post("/tickets", json=_ticket_payload(str(i))).json()["ticket_numero"]

    with ThreadPoolExecutor(max_workers=5) as executor:
        numeros = list(executor.map(create_one, range(10)))

    assert len(numeros) == len(set(numeros))
