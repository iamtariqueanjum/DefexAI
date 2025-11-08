import asyncio
import logging

from app.celery_app import app
from app.core.services.github_client import post_comment_to_github

logger = logging.getLogger(__name__)


@app.task(bind=True, name="defexai.post_comment_worker")
def post_comment_worker(self, payload: dict):
    """
    Celery task to post a comment to a GitHub PR.
    Args:
        payload: Dictionary containing:
            - repo: Repository name (e.g., "owner/repo")
            - pr_number: Pull request number
            - review_result: The review comment text to post
            - github_token: GitHub token for authentication
    
    Returns:
        Dictionary with status and details
    """
    try:
        # Log payload without exposing token
        payload_log = {k: v for k, v in payload.items() if k != "github_token"}
        payload_log["github_token"] = "***" if payload.get("github_token") else "MISSING"
        logger.info(f"Processing comment task for payload: {payload_log}")
        
        if not payload.get("github_token"):
            logger.error("ERROR: github_token is missing from payload!")
            raise ValueError("github_token is required")
        
        # Run async post_comment_to_github function in sync context
        asyncio.run(post_comment_to_github(payload))
        logger.info(f"Comment posted successfully to {payload.get('repo')} PR #{payload.get('pr_number')}")
        
        return {
            "status": "success",
            "repo": payload.get("repo"),
            "pr_number": payload.get("pr_number")
        }
    except Exception as e:
        logger.error(f"Error in post_comment_task: {e}", exc_info=True)
        raise
