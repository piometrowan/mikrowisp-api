from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

class ClientBase(BaseModel):
    """Esquema base para cliente"""
    nombre: str = Field(..., min_length=2, max_length=255, description="Nombre completo del cliente")
    cedula: Optional[str] = Field(None, description="Documento de identificación")
    correo: Optional[EmailStr] = Field(None, description="Email del cliente")
    telefono: Optional[str] = Field(None, description="Teléfono fijo")
    movil: Optional[str] = Field(None, description="Teléfono móvil")
    direccion_principal: Optional[str] = Field(None, description="Dirección principal")

class ClientCreate(ClientBase):
    """Esquema para crear cliente"""
    pass

class ClientUpdate(BaseModel):
    """Esquema para actualizar cliente"""
    nombre: Optional[str] = Field(None, min_length=2, max_length=255)
    correo: Optional[EmailStr] = None
    telefono: Optional[str] = None
    movil: Optional[str] = None
    cedula: Optional[str] = None
    codigo: Optional[str] = Field(None, description="Contraseña portal cliente")
    direccion_principal: Optional[str] = None
    campo_personalizado: Optional[str] = None

class ServiceInfo(BaseModel):
    """Información de servicio del cliente"""
    id: int
    idperfil: int
    nodo: int
    costo: str
    ipap: Optional[str]
    mac: Optional[str]
    ip: Optional[str]
    instalado: Optional[str]
    pppuser: Optional[str]
    ppppass: Optional[str]
    tiposervicio: str
    status_user: str
    coordenadas: Optional[str]
    direccion: Optional[str]
    snmp_comunidad: Optional[str]
    perfil: str

class BillingInfo(BaseModel):
    """Información de facturación del cliente"""
    facturas_nopagadas: int
    total_facturas: str

class ClientResponse(ClientBase):
    """Respuesta con información completa del cliente"""
    id: int
    estado: str
    codigo: str
    servicios: List[ServiceInfo] = []
    facturacion: Optional[BillingInfo] = None

class ClientListFilters(BaseModel):
    """Filtros para listar clientes"""
    idcliente: Optional[int] = None
    telefono: Optional[str] = None
    cedula: Optional[str] = None

class PreRegistrationCreate(BaseModel):
    """Esquema para crear pre-registro"""
    cliente: str = Field(..., description="Nombre completo del cliente")
    cedula: str = Field(..., description="Documento de identificación")
    direccion: str = Field(..., description="Dirección del cliente")
    telefono: Optional[str] = None
    movil: Optional[str] = None
    email: Optional[EmailStr] = None
    notas: Optional[str] = None
    fecha_instalacion: Optional[datetime] = None

class PreRegistrationFilters(BaseModel):
    """Filtros para listar pre-registros"""
    estado: Optional[str] = Field(None, description="PENDIENTE, NO INSTALADO, INSTALADO")
    cedula: Optional[str] = None

class ActivateClientRequest(BaseModel):
    """Esquema para activar/suspender cliente"""
    idcliente: int = Field(..., description="ID del cliente")

class MikrowispResponse(BaseModel):
    """Respuesta estándar de Mikrowisp"""
    estado: str
    mensaje: str
    idcliente: Optional[int] = None
    idregistro: Optional[int] = None