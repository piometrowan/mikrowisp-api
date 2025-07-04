from fastapi import APIRouter, HTTPException, Depends, status
import logging

from app.schemas.ticket import (
    TicketCreate, TicketClose, TicketListRequest,
    TicketCreateResponse, TicketListResponse
)
from app.services.mikrowisp_client import mikrowisp_client
from app.dependencies.auth import get_current_user
from app.dependencies.mikrowisp import validate_mikrowisp_response

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/tickets", tags=["Tickets"])


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_ticket(
        ticket_data: TicketCreate,
        current_user=Depends(get_current_user)
):
    """Crea un nuevo ticket de soporte"""
    try:
        response = await mikrowisp_client.create_ticket(ticket_data.dict(exclude_none=True))
        validate_mikrowisp_response(response)

        logger.info(f"Ticket creado exitosamente: {response.get('idticket')}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear ticket: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/client/{client_id}", response_model=dict)
async def list_client_tickets(
        client_id: int,
        current_user=Depends(get_current_user)
):
    """Lista todos los tickets de un cliente"""
    try:
        response = await mikrowisp_client.list_tickets(client_id)
        validate_mikrowisp_response(response)

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al listar tickets del cliente {client_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.put("/{ticket_id}/close", response_model=dict)
async def close_ticket(
        ticket_id: int,
        close_data: TicketClose,
        current_user=Depends(get_current_user)
):
    """Cierra un ticket existente"""
    try:
        if close_data.idticket != ticket_id:
            raise HTTPException(
                status_code=400,
                detail="El ID del ticket en la URL no coincide con el del cuerpo"
            )

        response = await mikrowisp_client.close_ticket(
            ticket_id,
            close_data.motivo_cierre
        )
        validate_mikrowisp_response(response)

        logger.info(f"Ticket {ticket_id} cerrado exitosamente")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al cerrar ticket {ticket_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")