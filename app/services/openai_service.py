import asyncio
from openai import AsyncOpenAI
from typing import Dict, List, Any, Optional
import json
import logging

from app.config.settings import settings

logger = logging.getLogger(__name__)


class OpenAIService:
    """Servicio para integración con OpenAI"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    async def process_client_query(
            self,
            query: str,
            client_context: Dict[str, Any] = None
    ) -> str:
        """Procesa consulta de cliente usando IA"""
        try:
            system_prompt = self._build_system_prompt(client_context)

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error en procesamiento de IA: {str(e)}")
            return "Lo siento, no pude procesar tu consulta en este momento."

    def _build_system_prompt(self, client_context: Dict[str, Any] = None) -> str:
        """Construye el prompt del sistema con contexto del cliente"""
        base_prompt = """Eres un asistente de atención al cliente para un proveedor de servicios de internet.
        Tu objetivo es ayudar a los clientes con sus consultas sobre servicios, facturas, soporte técnico y más.

        Responde de manera amigable, profesional y útil. Si necesitas información específica del cliente,
        pídesela de manera cortés."""

        if client_context:
            context_info = f"\n\nContexto del cliente:\n{json.dumps(client_context, indent=2, ensure_ascii=False)}"
            base_prompt += context_info

        return base_prompt

    async def generate_sms_content(
            self,
            message_type: str,
            client_data: Dict[str, Any] = None
    ) -> str:
        """Genera contenido para SMS usando IA"""
        try:
            prompt = f"""Genera un mensaje SMS profesional y amigable para {message_type}.
            El mensaje debe ser conciso (máximo 160 caracteres) y en español.

            Contexto del cliente: {json.dumps(client_data or {}, ensure_ascii=False)}

            Tipos de mensaje disponibles:
            - pago_recordatorio: Recordatorio de pago
            - pago_confirmacion: Confirmación de pago recibido
            - servicio_suspension: Notificación de suspensión
            - servicio_activacion: Confirmación de activación
            - cita_tecnica: Recordatorio de cita técnica
            - general: Mensaje general
            """

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=100
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error generando contenido SMS: {str(e)}")
            return "Estimado cliente, contacte con nosotros para más información."


# Instancia global del servicio
openai_service = OpenAIService()