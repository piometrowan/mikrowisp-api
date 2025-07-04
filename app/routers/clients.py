from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi.responses import JSONResponse
from typing import Optional, List
import logging

from app.schemas.client import (
    ClientCreate, ClientUpdate, ClientResponse, ClientListFilters,
    PreRegistrationCreate, PreRegistrationFilters, ActivateClientRequest,
    MikrowispResponse
)
from app.services.mikrowisp_client import mikrowisp_client
from app.dependencies.auth import get_current_user
from app.dependencies.mikrowisp import validate_mikrowisp_response

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/clients", tags=["Clientes"])


@router.post("/", response_model=MikrowispResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
        client_data: ClientCreate,
        current_user=Depends(get_current_user)
):
    """Crea un nuevo cliente en Mikrowisp"""
    try:
        response = await mikrowisp_client.create_client(client_data.dict(exclude_none=True))
        validate_mikrowisp_response(response)

        logger.info(f"Cliente creado exitosamente: {response.get('idcliente')}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado al crear cliente: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/{client_id}", response_model=dict)
async def get_client_by_id(
        client_id: int,
        current_user=Depends(get_current_user)
):
    """Obtiene detalles de un cliente por ID"""
    try:
        response = await mikrowisp_client.get_client_details(client_id=client_id)
        validate_mikrowisp_response(response)

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener cliente {client_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/", response_model=dict)
async def search_clients(
        cedula: Optional[str] = Query(None, description="Buscar por cédula"),
        telefono: Optional[str] = Query(None, description="Buscar por teléfono"),
        idcliente: Optional[int] = Query(None, description="Buscar por ID"),
        current_user=Depends(get_current_user)
):
    """Busca clientes con filtros opcionales"""
    try:
        filters = {}
        if cedula:
            filters["cedula"] = cedula
        if telefono:
            filters["telefono"] = telefono
        if idcliente:
            filters["idcliente"] = idcliente

        response = await mikrowisp_client.get_client_details(**filters)
        validate_mikrowisp_response(response)

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en búsqueda de clientes: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.put("/{client_id}", response_model=MikrowispResponse)
async def update_client(
        client_id: int,
        client_data: ClientUpdate,
        current_user=Depends(get_current_user)
):
    """Actualiza datos de un cliente"""
    try:
        update_data = client_data.dict(exclude_none=True)
        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="Debe proporcionar al menos un campo para actualizar"
            )

        response = await mikrowisp_client.update_client(client_id, update_data)
        validate_mikrowisp_response(response)

        logger.info(f"Cliente {client_id} actualizado exitosamente")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar cliente {client_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post("/{client_id}/activate", response_model=MikrowispResponse)
async def activate_client(
        client_id: int,
        current_user=Depends(get_current_user)
):
    """Activa un cliente suspendido"""
    try:
        response = await mikrowisp_client.activate_client(client_id)
        validate_mikrowisp_response(response)

        logger.info(f"Cliente {client_id} activado exitosamente")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al activar cliente {client_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post("/{client_id}/suspend", response_model=MikrowispResponse)
async def suspend_client(
        client_id: int,
        current_user=Depends(get_current_user)
):
    """Suspende un cliente activo"""
    try:
        response = await mikrowisp_client.suspend_client(client_id)
        validate_mikrowisp_response(response)

        logger.info(f"Cliente {client_id} suspendido exitosamente")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al suspender cliente {client_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post("/pre-registrations/", response_model=MikrowispResponse, status_code=status.HTTP_201_CREATED)
async def create_pre_registration(
        registration_data: PreRegistrationCreate,
        current_user=Depends(get_current_user)
):
    """Crea un pre-registro de instalación"""
    try:
        response = await mikrowisp_client.create_pre_registration(
            registration_data.dict(exclude_none=True)
        )
        validate_mikrowisp_response(response)

        logger.info(f"Pre-registro creado exitosamente: {response.get('idregistro')}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear pre-registro: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/installations/", response_model=dict)
async def list_installations(
        estado: Optional[str] = Query(None, description="PENDIENTE, NO INSTALADO, INSTALADO"),
        cedula: Optional[str] = Query(None, description="Filtrar por cédula"),
        current_user=Depends(get_current_user)
):
    """Lista instalaciones/pre-registros"""
    try:
        filters = {}
        if estado:
            filters["estado"] = estado
        if cedula:
            filters["cedula"] = cedula

        response = await mikrowisp_client.list_installations(filters)
        validate_mikrowisp_response(response)

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al listar instalaciones: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")