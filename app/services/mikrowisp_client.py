import httpx
import asyncio
from typing import Dict, List, Optional, Any
from fastapi import HTTPException
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)


class MikrowispClient:
    """Cliente asíncrono para interactuar con la API de Mikrowisp"""

    def __init__(self):
        self.base_url = settings.mikrowisp_base_url
        self.token = settings.mikrowisp_token
        self.timeout = settings.mikrowisp_timeout

    async def _make_request(
            self,
            endpoint: str,
            data: Dict[str, Any] = None,
            method: str = "POST"
    ) -> Dict[str, Any]:
        """Realiza peticiones HTTP a la API de Mikrowisp"""

        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_data = {"token": self.token}

        if data:
            request_data.update(data)

        headers = {"Content-Type": "application/json"}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method.upper() == "POST":
                    response = await client.post(url, json=request_data, headers=headers)
                else:
                    response = await client.get(url, params=request_data, headers=headers)

                response.raise_for_status()
                return response.json()

        except httpx.TimeoutException:
            logger.error(f"Timeout en solicitud a {endpoint}")
            raise HTTPException(status_code=408, detail="Timeout en solicitud a Mikrowisp")
        except httpx.HTTPStatusError as e:
            logger.error(f"Error HTTP {e.response.status_code} en {endpoint}: {e.response.text}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Error en Mikrowisp: {e.response.text}"
            )
        except Exception as e:
            logger.error(f"Error inesperado en {endpoint}: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    # Métodos para Clientes
    async def create_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nuevo cliente en Mikrowisp"""
        return await self._make_request("/api/v1/NewUser", client_data)

    async def get_client_details(self, client_id: Optional[int] = None,
                                 cedula: Optional[str] = None) -> Dict[str, Any]:
        """Obtiene detalles de un cliente"""
        data = {}
        if client_id:
            data["idcliente"] = client_id
        if cedula:
            data["cedula"] = cedula
        return await self._make_request("/api/v1/GetClientsDetails", data)

    async def update_client(self, client_id: int, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza datos de un cliente"""
        data = {"idcliente": client_id, "datos": client_data}
        return await self._make_request("/api/v1/UpdateUser", data)

    async def activate_client(self, client_id: int) -> Dict[str, Any]:
        """Activa un cliente"""
        data = {"idcliente": client_id}
        return await self._make_request("/api/v1/ActiveService", data)

    async def suspend_client(self, client_id: int) -> Dict[str, Any]:
        """Suspende un cliente"""
        data = {"idcliente": client_id}
        return await self._make_request("/api/v1/SuspendService", data)

    # Métodos para Facturas
    async def create_invoice(self, client_id: int, due_date: str) -> Dict[str, Any]:
        """Crea una nueva factura"""
        data = {"idcliente": client_id, "vencimiento": due_date}
        return await self._make_request("/api/v1/CreateInvoice", data)

    async def get_invoices(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Obtiene lista de facturas con filtros opcionales"""
        data = filters or {}
        return await self._make_request("/api/v1/GetInvoices", data)

    async def get_invoice(self, invoice_id: int) -> Dict[str, Any]:
        """Obtiene detalles de una factura específica"""
        data = {"idfactura": invoice_id}
        return await self._make_request("/api/v1/GetInvoice", data)

    async def pay_invoice(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Registra pago de una factura"""
        return await self._make_request("/api/v1/PaidInvoice", payment_data)

    async def delete_invoice(self, invoice_id: int) -> Dict[str, Any]:
        """Elimina una factura"""
        data = {"idfactura": invoice_id}
        return await self._make_request("/DeleteInvoice", data)

    # Métodos para Tickets
    async def create_ticket(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nuevo ticket de soporte"""
        return await self._make_request("/api/v1/NewTicket", ticket_data)

    async def close_ticket(self, ticket_id: int, reason: str = "") -> Dict[str, Any]:
        """Cierra un ticket"""
        data = {"idticket": ticket_id, "motivo_cierre": reason}
        return await self._make_request("/api/v1/CloseTicket", data)

    async def list_tickets(self, client_id: int) -> Dict[str, Any]:
        """Lista tickets de un cliente"""
        data = {"idcliente": client_id}
        return await self._make_request("/api/v1/ListTicket", data)

    # Métodos para Mensajería
    async def send_sms(self, client_id: int, message: str) -> Dict[str, Any]:
        """Envía SMS a un cliente"""
        data = {"idcliente": client_id, "mensaje": message}
        return await self._make_request("/api/v1/NewSMS", data)

    # Métodos para Pre-registros
    async def create_pre_registration(self, registration_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un pre-registro de instalación"""
        return await self._make_request("/api/v1/NewPreRegistro", registration_data)

    async def list_installations(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Lista instalaciones/pre-registros"""
        data = filters or {}
        return await self._make_request("/api/v1/ListInstall", data)

    # Métodos para Routers y Monitoreo
    async def get_routers(self, router_id: int = -1) -> Dict[str, Any]:
        """Obtiene lista de routers"""
        data = {"id": router_id}
        return await self._make_request("/api/v1/GetRouters", data)

    async def get_monitoring(self, equipment_id: int = -1) -> Dict[str, Any]:
        """Obtiene equipos en monitoreo"""
        data = {"id": equipment_id}
        return await self._make_request("/api/v1/GetMonitoreo", data)


# Instancia global del cliente
mikrowisp_client = MikrowispClient()