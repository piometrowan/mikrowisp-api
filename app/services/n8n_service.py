import httpx
import asyncio
from typing import Dict, Any
import logging

from app.config.settings import settings

logger = logging.getLogger(__name__)


class N8NService:
    """Servicio para integración con N8N"""

    def __init__(self):
        self.webhook_url = settings.n8n_webhook_url
        self.api_key = settings.n8n_api_key
        self.timeout = 30

    async def trigger_workflow(
            self,
            workflow_data: Dict[str, Any],
            workflow_type: str = "mikrowisp_integration"
    ) -> Dict[str, Any]:
        """Dispara un workflow en N8N"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            payload = {
                "workflow_type": workflow_type,
                "data": workflow_data,
                "timestamp": asyncio.get_event_loop().time()
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                return response.json()

        except httpx.TimeoutException:
            logger.error(f"Timeout en webhook N8N para {workflow_type}")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"Error HTTP en N8N: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado en N8N: {str(e)}")
            raise

    async def notify_client_created(self, client_data: Dict[str, Any]) -> None:
        """Notifica creación de cliente a N8N"""
        try:
            await self.trigger_workflow(client_data, "client_created")
            logger.info(f"Notificación de cliente creado enviada a N8N")
        except Exception as e:
            logger.error(f"Error notificando cliente creado: {str(e)}")

    async def notify_payment_received(self, payment_data: Dict[str, Any]) -> None:
        """Notifica pago recibido a N8N"""
        try:
            await self.trigger_workflow(payment_data, "payment_received")
            logger.info(f"Notificación de pago recibido enviada a N8N")
        except Exception as e:
            logger.error(f"Error notificando pago: {str(e)}")

    async def notify_ticket_created(self, ticket_data: Dict[str, Any]) -> None:
        """Notifica creación de ticket a N8N"""
        try:
            await self.trigger_workflow(ticket_data, "ticket_created")
            logger.info(f"Notificación de ticket creado enviada a N8N")
        except Exception as e:
            logger.error(f"Error notificando ticket: {str(e)}")


# Instancia global del servicio
n8n_service = N8NService()