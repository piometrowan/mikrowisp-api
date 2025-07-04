from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import Optional
import logging

from app.schemas.invoice import (
    InvoiceCreate, InvoiceFilters, PaymentCreate, PromisePaymentCreate,
    InvoiceResponse, InvoiceListResponse, DeleteInvoiceRequest, DeletePaymentRequest
)
from app.services.mikrowisp_client import mikrowisp_client
from app.dependencies.auth import get_current_user
from app.dependencies.mikrowisp import validate_mikrowisp_response

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/invoices", tags=["Facturas"])


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_invoice(
        invoice_data: InvoiceCreate,
        current_user=Depends(get_current_user)
):
    """Crea una nueva factura"""
    try:
        response = await mikrowisp_client.create_invoice(
            invoice_data.idcliente,
            invoice_data.vencimiento
        )
        validate_mikrowisp_response(response)

        logger.info(f"Factura creada exitosamente: {response.get('idfactura')}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear factura: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/", response_model=dict)
async def list_invoices(
        limit: Optional[int] = Query(25, ge=1, le=100, description="Límite de facturas"),
        estado: Optional[int] = Query(None, description="0=Pagadas, 1=No pagadas, 2=Anuladas"),
        idcliente: Optional[int] = Query(None, description="ID del cliente"),
        fechapago: Optional[str] = Query(None, description="Fecha de pago YYYY-MM-DD"),
        formapago: Optional[str] = Query(None, description="Forma de pago"),
        current_user=Depends(get_current_user)
):
    """Lista facturas con filtros opcionales"""
    try:
        filters = {"limit": limit}
        if estado is not None:
            filters["estado"] = estado
        if idcliente:
            filters["idcliente"] = idcliente
        if fechapago:
            filters["fechapago"] = fechapago
        if formapago:
            filters["formapago"] = formapago

        response = await mikrowisp_client.get_invoices(filters)
        validate_mikrowisp_response(response)

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al listar facturas: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/{invoice_id}", response_model=dict)
async def get_invoice(
        invoice_id: int,
        current_user=Depends(get_current_user)
):
    """Obtiene detalles de una factura específica"""
    try:
        response = await mikrowisp_client.get_invoice(invoice_id)
        validate_mikrowisp_response(response)

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener factura {invoice_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post("/payments/", response_model=dict)
async def pay_invoice(
        payment_data: PaymentCreate,
        current_user=Depends(get_current_user)
):
    """Registra el pago de una factura"""
    try:
        response = await mikrowisp_client.pay_invoice(payment_data.dict(exclude_none=True))
        validate_mikrowisp_response(response)

        logger.info(f"Pago registrado para factura: {payment_data.idfactura}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al registrar pago: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post("/promise-payments/", response_model=dict)
async def create_promise_payment(
        promise_data: PromisePaymentCreate,
        current_user=Depends(get_current_user)
):
    """Crea una promesa de pago"""
    try:
        response = await mikrowisp_client._make_request(
            "/api/v1/PromesaPago",
            promise_data.dict(exclude_none=True)
        )
        validate_mikrowisp_response(response)

        logger.info(f"Promesa de pago creada para factura: {promise_data.idfactura}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear promesa de pago: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.delete("/{invoice_id}", response_model=dict)
async def delete_invoice(
        invoice_id: int,
        current_user=Depends(get_current_user)
):
    """Elimina una factura no pagada"""
    try:
        response = await mikrowisp_client.delete_invoice(invoice_id)
        validate_mikrowisp_response(response)

        logger.info(f"Factura {invoice_id} eliminada exitosamente")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar factura {invoice_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.delete("/payments/{invoice_id}", response_model=dict)
async def delete_payment(
        invoice_id: int,
        current_user=Depends(get_current_user)
):
    """Elimina el pago de una factura"""
    try:
        response = await mikrowisp_client._make_request(
            "/api/v1/DeleteTransaccion",
            {"factura": invoice_id}
        )
        validate_mikrowisp_response(response)

        logger.info(f"Pago eliminado para factura: {invoice_id}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar pago: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")