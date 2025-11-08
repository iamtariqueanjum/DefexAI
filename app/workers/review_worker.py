import asyncio
import logging

from app.celery_app import app
from app.core.services.review_service import review_code
from app.core.utils.constants import QueueConstants
from app.core.utils.review_format import format_review_result

logger = logging.getLogger(__name__)


@app.task(bind=True, name="defexai.review_code_worker")
def review_code_worker(self, payload: dict):
    """
    Celery task to review code and dispatch comment task.
    Args:
        payload: Dictionary containing:
            - repo: Repository name (e.g., "owner/repo")
            - pr_number: Pull request number
            - base: Base branch name
            - head: Head branch name
            - github_token: GitHub token for authentication
            - diff: (optional) Pre-fetched diff text
            - max_bytes: (optional) Maximum bytes to fetch for diff
    Returns:
        Dictionary with status and review result
    """
    try:
        # Log payload without exposing full token
        payload_log = {k: v for k, v in payload.items() if k != "github_token"}
        payload_log["github_token"] = f"{payload.get('github_token', '')[:7]}...***" if payload.get("github_token") else "MISSING"
        logger.info(f"Processing review task for payload: {payload_log}")
        
        if not payload.get("github_token"):
            logger.warning("WARNING: github_token is missing from review payload!")
        
        # Run async review_code function in sync context
        review_result = asyncio.run(review_code(payload))
        logger.info(f"Review completed for {payload.get('repo')} PR #{payload.get('pr_number')}")
        
        # Format review result as a readable comment string
        review_comment = format_review_result(review_result)
        
        github_token = payload.get("github_token")
        if not github_token:
            logger.error("ERROR: Cannot publish to comment queue - github_token is missing!")
            raise ValueError("github_token is required to publish comment")
        
        # Directly dispatch Celery task instead of publishing to RabbitMQ
        # This avoids async/sync mixing issues and is more efficient
        from app.workers.comment_worker import post_comment_worker
        
        comment_payload = {
            "repo": payload.get("repo"),
            "pr_number": payload.get("pr_number"),
            "review_result": review_comment,
            "github_token": github_token
        }
        
        post_comment_worker.apply_async(
            args=[comment_payload], 
            queue=QueueConstants.GITHUB_COMMENT_QUEUE)
        logger.info("Review result dispatched to comment worker task")
        
        return {
            "status": "success",
            "review_result": review_result,
            "comment_queued": True
        }
    except Exception as e:
        logger.error(f"Error in review_code_task: {e}", exc_info=True)
        raise
