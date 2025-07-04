from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import uvicorn
from contextlib import asynccontextmanager

from app.config.settings import settings
from app.middleware.logging import LoggingMiddleware
from app.routers import clients, invoices, tickets, messaging, monitoring
from app.routers.auth import router as auth_router

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=settings.log_file if settings.log_file else None
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejo del ciclo de vida de la aplicación"""
    # Startup
    logger.info("Iniciando Mikrowisp Integration API...")
    logger.info(f"Conectando a Mikrowisp: {settings.mikrowisp_base_url}")

    yield

    # Shutdown
    logger.info("Cerrando Mikrowisp Integration API...")


# Crear aplicación FastAPI
app = FastAPI(
    title="Mikrowisp Integration API",
    description="API para integración con Mikrowisp CRM",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Añadir middleware de logging
app.add_middleware(LoggingMiddleware)


# Manejador global de excepciones
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Manejador personalizado de excepciones HTTP"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code,
            "timestamp": str(time.time())
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Manejador para excepciones no controladas"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.error(f"[{request_id}] Excepción no controlada: {str(exc)}")

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Error interno del servidor",
            "request_id": request_id
        }
    )


# Incluir routers
app.include_router(auth_router, prefix="/auth", tags=["Autenticación"])
app.include_router(clients.router)
app.include_router(invoices.router)
app.include_router(tickets.router)
app.include_router(messaging.router)
app.include_router(monitoring.router)


# Endpoint de salud
@app.get("/health", tags=["Sistema"])
async def health_check():
    """Endpoint para verificar el estado de la API"""
    return {
        "status": "healthy",
        "service": "Mikrowisp Integration API",
        "version": "1.0.0",
        "mikrowisp_url": settings.mikrowisp_base_url
    }


# Endpoint para procesar mensajes (equivalente al endpoint original)
@app.post("/mensajes/procesar", tags=["Mensajería"])
async def process_messages(request_data: dict):
    """Procesa mensajes desde N8N u otros servicios"""
    try:
        from app.services.openai_service import openai_service
        from app.services.n8n_service import n8n_service

        # Extraer datos del mensaje
        message_data = request_data.get("data", {})
        mikrowisp_installation = request_data.get("mikrowisp_installation", "default")

        # Procesar con IA si es necesario
        if message_data.get("input"):
            ai_response = await openai_service.process_client_query(
                message_data["input"],
                message_data.get("client_context")
            )

            # Enviar respuesta a N8N
            await n8n_service.trigger_workflow({
                "response": ai_response,
                "original_data": message_data
            }, "ai_response")

            return {"status": "processed", "response": ai_response}

        return {"status": "no_processing_needed"}

    except Exception as e:
        logger.error(f"Error procesando mensaje: {str(e)}")
        raise HTTPException(status_code=500, detail="Error procesando mensaje")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )