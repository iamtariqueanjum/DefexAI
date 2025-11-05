import aio_pika
import asyncio
import json

from app.core.rabbit_mq.connection import get_connection
from app.core.services.review_service import review_code
from app.core.utils.constants import QueueConstants


async def main():
    connection = await get_connection()
    channel = await connection.channel()
    queue = await channel.declare_queue(QueueConstants.CODE_REVIEW_QUEUE, durable=True)
    print("Worker is ready to receive messages....")
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                payload = json.loads(message.body)
                print(f"Received review task for payload: {payload}")
                review_result = await review_code(payload)
                # await publish_message(QueueConstants.COMMENT_QUEUE, {
                #     "repo": payload.get("repo"),
                #     "pr_number": payload.get("pr_number"),
                #     "review_result": review_result
                # })
                print("Review done: ", review_result)
                

    
if __name__ == "__main__":
    asyncio.run(main())
