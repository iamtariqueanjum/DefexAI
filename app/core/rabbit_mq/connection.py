import aio_pika
import asyncio
import os

from app.core.utils.constants import RabbitMQConstants

async def get_connection():
    return await aio_pika.connect_robust(RabbitMQConstants.RABBITMQ_URL)