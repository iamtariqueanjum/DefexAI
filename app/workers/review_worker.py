import asyncio
import json

from app.core.rabbit_mq.connection import get_connection
from app.core.rabbit_mq.publisher import publish_message
from app.core.services.review_service import review_code
from app.core.utils.constants import QueueConstants
from app.core.utils.review_format import format_review_result


async def main():
    connection = await get_connection()
    channel = await connection.channel()
    queue = await channel.declare_queue(QueueConstants.CODE_REVIEW_QUEUE, durable=True)
    print(f"Review Worker is ready to receive messages from queue: {QueueConstants.CODE_REVIEW_QUEUE}")
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            try:
                async with message.process():
                    payload = json.loads(message.body)
                    # Log payload without exposing full token
                    payload_log = {k: v for k, v in payload.items() if k != "github_token"}
                    payload_log["github_token"] = f"{payload.get('github_token', '')[:7]}...***" if payload.get("github_token") else "MISSING"
                    print(f"Received review task for payload: {payload_log}")
                    
                    if not payload.get("github_token"):
                        print("WARNING: github_token is missing from review payload!")
                    
                    review_result = await review_code(payload)
                    print("Review done: ", review_result)
                    
                    # Format review result as a readable comment string
                    review_comment = format_review_result(review_result)
                    
                    github_token = payload.get("github_token")
                    if not github_token:
                        print("ERROR: Cannot publish to comment queue - github_token is missing!")
                    
                    await publish_message(QueueConstants.COMMENT_QUEUE, {
                        "repo": payload.get("repo"),
                        "pr_number": payload.get("pr_number"),
                        "review_result": review_comment,
                        "github_token": github_token
                    })
                    print(f"Review submitted to comment worker queue: {QueueConstants.COMMENT_QUEUE}")
            except Exception as e:
                print(f"Error processing review message: {e}")
                import traceback
                traceback.print_exc()


    
if __name__ == "__main__":
    asyncio.run(main())
