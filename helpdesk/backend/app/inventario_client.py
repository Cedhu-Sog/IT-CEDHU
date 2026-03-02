import os
from typing import Any

import requests


class InventarioClient:
    def __init__(self) -> None:
        self.base_url = os.getenv("INVENTARIO_API_BASE_URL", "").rstrip("/")
        self.token = os.getenv("INVENTARIO_API_TOKEN", "")
        self.timeout = int(os.getenv("INVENTARIO_API_TIMEOUT", "5"))

    def _headers(self) -> dict[str, str]:
        if not self.token:
            return {}
        return {"Authorization": f"Bearer {self.token}"}

    def _get_optional(self, path: str) -> list[dict[str, Any]]:
        if not self.base_url:
            return []
        url = f"{self.base_url}{path}"
        try:
            response = requests.get(url, headers=self._headers(), timeout=self.timeout)
            if response.status_code >= 400:
                return []
            data = response.json()
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                for key in ("results", "data", "items"):
                    if isinstance(data.get(key), list):
                        return data[key]
            return []
        except Exception:
            return []

    def obtener_ubicaciones(self) -> list[dict[str, Any]]:
        return self._get_optional("/inventario/ubicaciones")

    def obtener_usuarios(self) -> list[dict[str, Any]]:
        usuarios = self._get_optional("/inventario/usuarios")
        if usuarios:
            return usuarios
        return self._get_optional("/inventario/personas")
