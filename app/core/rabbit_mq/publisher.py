
import json
import aio_pika
from app.core.rabbit_mq.connection import get_connection


async def publish_message(queue_name: str, payload: dict):
    connection = await get_connection()
    channel = await connection.channel()
    await channel.declare_queue(queue_name, durable=True)

    message = aio_pika.Message(
        body=json.dumps(payload).encode(),
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT
    )

    await channel.default_exchange.publish(message, routing_key=queue_name)
    await connection.close()

    print(f"Published message to {queue_name} queue with payload: {payload}")



