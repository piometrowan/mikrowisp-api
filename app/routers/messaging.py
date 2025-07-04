from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
import logging

from app.services.mikrowisp_client import mikrowisp_client
from app.dependencies.auth import get_current_user
from app.dependencies.mikrowisp import validate_mikrowisp_response

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/messaging", tags=["Mensajería"])


class SMSRequest(BaseModel):
    """Esquema para envío de SMS"""
    idcliente: int = Field(..., description="ID del cliente")
    mensaje: str = Field(..., min_length=1, max_length=160, description="Mensaje a enviar")


@router.post("/sms", response_model=dict)
async def send_sms(
        sms_data: SMSRequest,
        current_user=Depends(get_current_user)
):
    """Envía un SMS a un cliente"""
    try:
        response = await mikrowisp_client.send_sms(
            sms_data.idcliente,
            sms_data.mensaje
        )
        validate_mikrowisp_response(response)

        logger.info(f"SMS enviado exitosamente al cliente: {sms_data.idcliente}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al enviar SMS: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")