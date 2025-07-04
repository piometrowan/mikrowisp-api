from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
import logging

from app.services.mikrowisp_client import mikrowisp_client
from app.dependencies.auth import get_current_user
from app.dependencies.mikrowisp import validate_mikrowisp_response

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/monitoring", tags=["Monitoreo"])


@router.get("/routers", response_model=dict)
async def get_routers(
        router_id: Optional[int] = Query(-1, description="ID del router (-1 para todos)"),
        current_user=Depends(get_current_user)
):
    """Obtiene información de routers"""
    try:
        response = await mikrowisp_client.get_routers(router_id)
        validate_mikrowisp_response(response)

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener routers: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/equipment", response_model=dict)
async def get_monitoring_equipment(
        equipment_id: Optional[int] = Query(-1, description="ID del equipo (-1 para todos)"),
        current_user=Depends(get_current_user)
):
    """Obtiene equipos en monitoreo"""
    try:
        response = await mikrowisp_client.get_monitoring(equipment_id)
        validate_mikrowisp_response(response)

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener equipos en monitoreo: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")