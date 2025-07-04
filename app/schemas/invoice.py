from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date

class InvoiceCreate(BaseModel):
    """Esquema para crear factura"""
    idcliente: int = Field(..., description="ID del cliente")
    vencimiento: str = Field(..., description="Fecha de vencimiento YYYY-MM-DD")

class InvoiceFilters(BaseModel):
    """Filtros para listar facturas"""
    limit: Optional[int] = Field(25, ge=1, le=100, description="Límite de facturas")
    estado: Optional[int] = Field(None, description="0=Pagadas, 1=No pagadas, 2=Anuladas")
    idcliente: Optional[int] = None
    fechapago: Optional[str] = Field(None, description="Fecha de pago YYYY-MM-DD")
    formapago: Optional[str] = None

class PaymentCreate(BaseModel):
    """Esquema para registrar pago"""
    idfactura: int = Field(..., description="ID de la factura")
    pasarela: str = Field(..., description="Nombre de la pasarela de pago")
    cantidad: Optional[float] = Field(None, description="Cantidad pagada")
    comision: Optional[float] = Field(None, description="Comisión del pago")
    idtransaccion: Optional[str] = Field(None, description="ID de transacción")
    fecha: Optional[str] = Field(None, description="Fecha del pago YYYY-MM-DD HH:mm:ss")

class PromisePaymentCreate(BaseModel):
    """Esquema para promesa de pago"""
    idfactura: int = Field(..., description="ID de la factura")
    fechalimite: str = Field(..., description="Fecha límite YYYY-MM-DD (máximo 20 días)")
    descripcion: Optional[str] = Field(None, description="Descripción de la promesa")

class InvoiceResponse(BaseModel):
    """Respuesta de factura"""
    id: int
    legal: int
    idcliente: int
    emitido: str
    vencimiento: str
    total: str
    estado: str
    cobrado: str
    impuesto: str
    oxxo_referencia: str
    barcode_cobro_digital: str
    fechapago: str
    subtotal: str
    subtotal2: str
    total2: str
    impuesto2: str
    formapago: str

class InvoiceListResponse(BaseModel):
    """Respuesta de lista de facturas"""
    estado: str
    facturas: List[InvoiceResponse]

class DeleteInvoiceRequest(BaseModel):
    """Esquema para eliminar factura"""
    idfactura: int = Field(..., description="ID de la factura")

class DeletePaymentRequest(BaseModel):
    """Esquema para eliminar pago"""
    factura: int = Field(..., description="ID de la factura")