import asyncio
import json

from app.core.rabbit_mq.connection import get_connection
from app.core.rabbit_mq.publisher import publish_message
from app.core.services.review_service import review_code
from app.core.utils.constants import QueueConstants


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
                    print(f"Received review task for payload: {payload}")
                    review_result = await review_code(payload)
                    print("Review done: ", review_result)
                    
                    # Format review result as a readable comment string
                    issues = review_result.get("issues", [])
                    if issues:
                        comment_lines = ["## Code Review Results\n"]
                        for issue in issues:
                            issue_type = issue.get("type", "other")
                            description = issue.get("description", "")
                            line_numbers = issue.get("line_numbers", [])
                            suggested_fix = issue.get("suggested_fix", "")
                            
                            comment_lines.append(f"### {issue_type.upper()}")
                            if line_numbers:
                                comment_lines.append(f"**Lines:** {', '.join(map(str, line_numbers))}")
                            comment_lines.append(f"**Issue:** {description}")
                            if suggested_fix:
                                comment_lines.append(f"**Suggestion:** {suggested_fix}")
                            comment_lines.append("")
                        
                        if review_result.get("truncated"):
                            comment_lines.append("_Note: Diff was truncated due to size limits._")
                        
                        review_comment = "\n".join(comment_lines)
                    else:
                        review_comment = "## Code Review Results\n\n✅ No issues found!"
                    
                    await publish_message(QueueConstants.COMMENT_QUEUE, {
                        "repo": payload.get("repo"),
                        "pr_number": payload.get("pr_number"),
                        "review_result": review_comment
                    })
                    print(f"Review submitted to comment worker queue: {QueueConstants.COMMENT_QUEUE}")
            except Exception as e:
                print(f"Error processing review message: {e}")
                import traceback
                traceback.print_exc()


    
if __name__ == "__main__":
    asyncio.run(main())
