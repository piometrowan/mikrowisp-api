from fastapi import Request, Response
from fastapi.responses import JSONResponse
import time
import logging
import uuid
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para logging de peticiones HTTP"""

    async def dispatch(self, request: Request, call_next):
        # Generar ID único para la petición
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Log de petición entrante
        start_time = time.time()
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )

        try:
            # Procesar petición
            response = await call_next(request)

            # Calcular tiempo de procesamiento
            process_time = time.time() - start_time

            # Log de respuesta
            logger.info(
                f"[{request_id}] {response.status_code} - "
                f"Processed in {process_time:.4f}s"
            )

            # Añadir header con request ID
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            # Log de error
            process_time = time.time() - start_time
            logger.error(
                f"[{request_id}] ERROR: {str(e)} - "
                f"Failed after {process_time:.4f}s"
            )

            # Retornar respuesta de error
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Error interno del servidor",
                    "request_id": request_id
                },
                headers={"X-Request-ID": request_id}
            )