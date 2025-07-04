# Mikrowisp Integration API

API moderna construida con FastAPI para integrar Mikrowisp CRM con servicios de IA y automatización.

## Características

- ✅ Integración completa con Mikrowisp API
- ✅ Autenticación JWT
- ✅ Procesamiento de IA con OpenAI
- ✅ Integración con N8N
- ✅ Colas de mensajes con RabbitMQ
- ✅ Cache con Redis
- ✅ Documentación automática
- ✅ Dockerizado
- ✅ Logging estructurado
- ✅ Rate limiting
- ✅ Manejo de errores robusto

## Instalación Rápida con Docker

1. Clonar el repositorio:
```bash
git clone https://github.com/piometrowan/mikrowisp-api.git
cd mikrowisp-api
```

2. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

3. Ejecutar con Docker Compose:
```bash
docker-compose up -d
```

4. Verificar que funciona:
```bash
curl http://localhost:8000/health
```

## Instalación Manual

### Prerrequisitos

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- RabbitMQ 3.12+

### Pasos

1. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

4. Ejecutar la aplicación:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Configuración

### Variables de Entorno Principales

| Variable | Descripción | Requerido |
|----------|-------------|-----------|
| `MIKROWISP_BASE_URL` | URL base de tu instancia Mikrowisp | ✅ |
| `MIKROWISP_TOKEN` | Token de API de Mikrowisp | ✅ |
| `JWT_SECRET_KEY` | Clave secreta para JWT | ✅ |
| `OPENAI_API_KEY` | API key de OpenAI | ✅ |
| `DATABASE_URL` | URL de conexión a PostgreSQL | ✅ |
| `N8N_WEBHOOK_URL` | URL del webhook de N8N | ⚠️ |
| `REDIS_URL` | URL de conexión a Redis | ⚠️ |
| `RABBITMQ_URL` | URL de conexión a RabbitMQ | ⚠️ |

## Uso

### Autenticación

1. Obtener token JWT:
```bash
curl -X POST "http://localhost:8000/auth/login" \
     -u "admin:admin123"
```

2. Usar token en requests:
```bash
curl -H "Authorization: Bearer <token>" \
     "http://localhost:8000/api/v1/clients/"
```

### Endpoints Principales

- **Clientes**: `/api/v1/clients/`
- **Facturas**: `/api/v1/invoices/`
- **Tickets**: `/api/v1/tickets/`
- **Mensajería**: `/api/v1/messaging/`
- **Monitoreo**: `/api/v1/monitoring/`

### Documentación API

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Desarrollo

### Estructura del Proyecto

```
app/
├── main.py              # Aplicación principal
├── config/              # Configuración
├── models/              # Modelos de base de datos
├── schemas/             # Esquemas Pydantic
├── routers/             # Endpoints organizados
├── services/            # Lógica de negocio
├── dependencies/        # Dependencias reutilizables
├── middleware/          # Middleware personalizado
└── utils/              # Utilidades
```

### Ejecutar Tests

```bash
pytest tests/ -v
```

### Linting y Formato

```bash
black app/
flake8 app/
```

## Despliegue en Producción

### Usando Docker

```bash
docker build -t mikrowisp-api .
docker run -d -p 8000:8000 --env-file .env mikrowisp-api
```

### Usando Docker Compose

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Configuraciones de Producción

1. Usar HTTPS (configurar certificados SSL)
2. Configurar proxy reverso (Nginx incluido)
3. Configurar monitoreo (Prometheus/Grafana)
4. Configurar backup de base de datos
5. Configurar logging centralizado

## Monitoreo

- Health check: `GET /health`
- Métricas: `GET /metrics` (si Prometheus está habilitado)
- Logs: Revisar logs del contenedor o archivo configurado

## Soporte

Para soporte técnico:
- Crear issue en GitHub
- Contactar al equipo de desarrollo
- Revisar documentación en `/docs`
```