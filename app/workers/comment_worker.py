import asyncio
import json

from app.core.rabbit_mq.connection import get_connection
from app.core.services.github_client import post_comment_to_github
from app.core.utils.constants import QueueConstants


async def main():
    connection = await get_connection()
    channel = await connection.channel()
    queue = await channel.declare_queue(QueueConstants.COMMENT_QUEUE, durable=True)
    print(f"Comment Worker is ready to receive messages from queue: {QueueConstants.COMMENT_QUEUE}")
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            try:
                async with message.process():
                    payload = json.loads(message.body)
                    # Log payload without exposing token
                    payload_log = {k: v for k, v in payload.items() if k != "github_token"}
                    payload_log["github_token"] = "***" if payload.get("github_token") else "MISSING"
                    print(f"Comment post task for payload: {payload_log}")
                    
                    if not payload.get("github_token"):
                        print("ERROR: github_token is missing from payload!")
                    
                    await post_comment_to_github(payload)
                    print("Comment posted successfully")
            except Exception as e:
                print(f"Error processing message: {e}")
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())