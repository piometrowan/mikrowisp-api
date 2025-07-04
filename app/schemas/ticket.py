from pydantic import BaseModel, Field
from typing import Optional, List

class TicketCreate(BaseModel):
    """Esquema para crear ticket"""
    idcliente: int = Field(..., description="ID del cliente")
    dp: int = Field(1, description="ID Departamento (1: Soporte Técnico)")
    asunto: str = Field(..., description="Asunto del ticket")
    solicitante: Optional[str] = Field(None, description="Nombre del solicitante")
    fechavisita: str = Field(..., description="Fecha de visita YYYY-MM-DD")
    turno: str = Field(..., description="TARDE o MAÑANA")
    agendado: str = Field(..., description="oficina, cliente, VIA TELEFONICA, PRESENCIAL, PAGINA WEB, RED SOCIAL")
    contenido: str = Field(..., description="Contenido del ticket")

class TicketClose(BaseModel):
    """Esquema para cerrar ticket"""
    idticket: int = Field(..., description="ID del ticket")
    motivo_cierre: Optional[str] = Field("", description="Motivo del cierre")

class TicketListRequest(BaseModel):
    """Esquema para listar tickets"""
    idcliente: int = Field(..., description="ID del cliente")

class TicketInfo(BaseModel):
    """Información de ticket"""
    id: int
    idcliente: int
    asunto: str
    fecha_soporte: str
    estado: str
    fecha_cerrado: str
    solicitante: str
    fechavisita: str
    turno: str
    agendado: str
    lastdate: str
    dp: str
    motivo_cierre: str

class TicketStats(BaseModel):
    """Estadísticas de tickets"""
    abiertos: int
    cerrados: int
    respondidos: int
    respuesta_cliente: int

class TicketListResponse(BaseModel):
    """Respuesta de lista de tickets"""
    estado: str
    mensaje: str
    data: dict = Field(..., description="Contiene 'abiertos', 'cerrados', etc. y 'tickets'")

class TicketCreateResponse(BaseModel):
    """Respuesta de creación de ticket"""
    estado: str
    idticket: str
    mensaje: str