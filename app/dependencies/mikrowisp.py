from fastapi import HTTPException, status
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def validate_mikrowisp_response(response: Dict[str, Any]) -> None:
    """Valida la respuesta de Mikrowisp y lanza excepción si hay error"""

    if not isinstance(response, dict):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Respuesta inválida de Mikrowisp"
        )

    estado = response.get("estado", "").lower()

    if estado != "exito":
        mensaje = response.get("mensaje", "Error desconocido en Mikrowisp")
        logger.warning(f"Error en Mikrowisp: {mensaje}")

        # Mapear errores específicos de Mikrowisp a códigos HTTP apropiados
        if "no encontrado" in mensaje.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=mensaje
            )
        elif "ya existe" in mensaje.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=mensaje
            )
        elif "inválido" in mensaje.lower() or "incorrecto" in mensaje.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=mensaje
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=mensaje
            )


def validate_client_permissions(client_id: int, current_user: Dict[str, Any]) -> None:
    """Valida permisos del usuario para acceder a un cliente específico"""

    # Si es admin, puede acceder a todo
    if current_user.get("is_admin", False):
        return

    # Si es cliente, solo puede acceder a sus propios datos
    user_client_id = current_user.get("client_id")
    if user_client_id and user_client_id != client_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para acceder a este cliente"
        )

    # Si no es admin ni cliente, denegar acceso
    if not user_client_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permisos insuficientes"
        )