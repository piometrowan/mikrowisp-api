import asyncio
import json
import logging
from datetime import datetime
import pika
from pika.adapters.asyncio_connection import AsyncioConnection

from app.config.settings import settings
from app.services.mikrowisp_client import mikrowisp_client
from app.services.openai_service import openai_service
from app.services.n8n_service import n8n_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MikrowispWorker:
    """Worker para procesar mensajes de RabbitMQ"""

    def __init__(self):
        self.connection = None
        self.channel = None
        self.should_reconnect = False
        self.was_consuming = False

    async def connect(self):
        """Conecta a RabbitMQ"""
        logger.info("Conectando a RabbitMQ...")

        parameters = pika.URLParameters(settings.rabbitmq_url)
        self.connection = AsyncioConnection(
            parameters,
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed
        )

    def on_connection_open(self, _unused_connection):
        """Callback cuando la conexión se abre"""
        logger.info("Conexión a RabbitMQ establecida")
        self.connection.channel(on_open_callback=self.on_channel_open)

    def on_connection_open_error(self, _unused_connection, err):
        """Callback cuando falla la conexión"""
        logger.error(f"Error conectando a RabbitMQ: {err}")
        self.reconnect()

    def on_connection_closed(self, _unused_connection, reason):
        """Callback cuando se cierra la conexión"""
        self.channel = None
        if self.should_reconnect:
            logger.warning(f"Conexión cerrada, reconectando en 5s: {reason}")
            self.connection.ioloop.call_later(5, self.reconnect)

    def on_channel_open(self, channel):
        """Callback cuando el canal se abre"""
        logger.info("Canal RabbitMQ abierto")
        self.channel = channel
        self.channel.add_on_close_callback(self.on_channel_closed)
        self.setup_queue()

    def on_channel_closed(self, channel, reason):
        """Callback cuando se cierra el canal"""
        logger.warning(f"Canal cerrado: {reason}")
        self.channel = None

    def setup_queue(self):
        """Configura la cola"""
        logger.info(f"Declarando cola: {settings.rabbitmq_queue}")
        self.channel.queue_declare(
            queue=settings.rabbitmq_queue,
            durable=True,
            callback=self.on_queue_declareok
        )

    def on_queue_declareok(self, _unused_frame):
        """Callback cuando la cola está declarada"""
        logger.info("Cola declarada, configurando QoS")
        self.channel.basic_qos(prefetch_count=1, callback=self.on_basic_qos_ok)

    def on_basic_qos_ok(self, _unused_frame):
        """Callback cuando QoS está configurado"""
        logger.info("QoS configurado, iniciando consumo")
        self.start_consuming()

    def start_consuming(self):
        """Inicia el consumo de mensajes"""
        logger.info("Iniciando consumo de mensajes")
        self.was_consuming = True
        self.channel.basic_consume(
            queue=settings.rabbitmq_queue,
            on_message_callback=self.on_message
        )

    async def on_message(self, channel, method, properties, body):
        """Procesa mensaje recibido"""
        try:
            # Decodificar mensaje
            message_data = json.loads(body.decode('utf-8'))
            logger.info(f"Procesando mensaje: {message_data.get('type', 'unknown')}")

            # Procesar según tipo de mensaje
            await self.process_message(message_data)

            # Confirmar mensaje procesado
            channel.basic_ack(delivery_tag=method.delivery_tag)
            logger.info("Mensaje procesado exitosamente")

        except json.JSONDecodeError:
            logger.error("Error decodificando JSON del mensaje")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            logger.error(f"Error procesando mensaje: {str(e)}")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    async def process_message(self, message_data: dict):
        """Procesa diferentes tipos de mensajes"""
        message_type = message_data.get('type')
        data = message_data.get('data', {})

        if message_type == 'client_query':
            await self.process_client_query(data)
        elif message_type == 'auto_sms':
            await self.process_auto_sms(data)
        elif message_type == 'payment_reminder':
            await self.process_payment_reminder(data)
        elif message_type == 'sync_data':
            await self.process_data_sync(data)
        else:
            logger.warning(f"Tipo de mensaje desconocido: {message_type}")

    async def process_client_query(self, data: dict):
        """Procesa consulta de cliente"""
        try:
            query = data.get('query', '')
            client_id = data.get('client_id')

            # Obtener contexto del cliente si está disponible
            client_context = None
            if client_id:
                try:
                    client_response = await mikrowisp_client.get_client_details(client_id=client_id)
                    client_context = client_response.get('datos', [])
                except Exception as e:
                    logger.warning(f"No se pudo obtener contexto del cliente {client_id}: {e}")

            # Procesar con IA
            ai_response = await openai_service.process_client_query(query, client_context)

            # Enviar respuesta a N8N
            await n8n_service.trigger_workflow({
                'client_id': client_id,
                'query': query,
                'response': ai_response,
                'timestamp': datetime.utcnow().isoformat()
            }, 'client_response')

        except Exception as e:
            logger.error(f"Error procesando consulta de cliente: {e}")

    async def process_auto_sms(self, data: dict):
        """Procesa envío automático de SMS"""
        try:
            client_id = data.get('client_id')
            message_type = data.get('message_type', 'general')
            custom_message = data.get('custom_message')

            if custom_message:
                message = custom_message
            else:
                # Generar mensaje con IA
                client_data = data.get('client_data', {})
                message = await openai_service.generate_sms_content(message_type, client_data)

            # Enviar SMS
            result = await mikrowisp_client.send_sms(client_id, message)

            # Notificar a N8N
            await n8n_service.trigger_workflow({
                'client_id': client_id,
                'message': message,
                'result': result
            }, 'sms_sent')

        except Exception as e:
            logger.error(f"Error enviando SMS automático: {e}")

    async def process_payment_reminder(self, data: dict):
        """Procesa recordatorio de pago"""
        try:
            client_id = data.get('client_id')

            # Obtener facturas pendientes
            invoices = await mikrowisp_client.get_invoices({
                'idcliente': client_id,
                'estado': 1  # No pagadas
            })

            if invoices.get('facturas'):
                # Generar mensaje de recordatorio
                message = await openai_service.generate_sms_content(
                    'pago_recordatorio',
                    {'client_id': client_id, 'invoices': invoices['facturas']}
                )

                # Enviar SMS
                await mikrowisp_client.send_sms(client_id, message)

                # Notificar a N8N
                await n8n_service.trigger_workflow({
                    'client_id': client_id,
                    'reminder_sent': True,
                    'pending_invoices': len(invoices['facturas'])
                }, 'payment_reminder_sent')

        except Exception as e:
            logger.error(f"Error procesando recordatorio de pago: {e}")

    async def process_data_sync(self, data: dict):
        """Procesa sincronización de datos"""
        try:
            sync_type = data.get('sync_type', 'full')

            if sync_type == 'clients':
                # Sincronizar datos de clientes
                await self.sync_clients_data()
            elif sync_type == 'invoices':
                # Sincronizar facturas
                await self.sync_invoices_data()
            elif sync_type == 'full':
                # Sincronización completa
                await self.sync_clients_data()
                await self.sync_invoices_data()

        except Exception as e:
            logger.error(f"Error en sincronización de datos: {e}")

    async def sync_clients_data(self):
        """Sincroniza datos de clientes"""
        logger.info("Iniciando sincronización de clientes")
        # Implementar lógica de sincronización según necesidades
        pass

    async def sync_invoices_data(self):
        """Sincroniza datos de facturas"""
        logger.info("Iniciando sincronización de facturas")
        # Implementar lógica de sincronización según necesidades
        pass

    def reconnect(self):
        """Reconecta a RabbitMQ"""
        self.should_reconnect = True
        self.connection.ioloop.stop()

    def close_connection(self):
        """Cierra la conexión"""
        if self.connection and not self.connection.is_closed:
            logger.info("Cerrando conexión a RabbitMQ")
            self.connection.close()


async def main():
    """Función principal del worker"""
    worker = MikrowispWorker()

    try:
        # Conectar y mantener el worker corriendo
        await worker.connect()

        # Mantener el worker corriendo
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        logger.info("Cerrando worker...")
        worker.close_connection()
    except Exception as e:
        logger.error(f"Error en worker: {e}")
        worker.close_connection()


if __name__ == "__main__":
    asyncio.run(main())