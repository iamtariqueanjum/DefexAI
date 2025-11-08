
from fastapi import APIRouter, HTTPException
import logging

from app.core.models.models import ReviewRequest
from app.core.utils.constants import QueueConstants
from app.workers.review_worker import review_code_worker


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/code/review")
async def analyze_code(payload: dict):
    try:
        review_request = ReviewRequest(**payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid payload: {str(e)}")
    
    # Validate required fields
    required_fields = ["repo", "pr_number", "base", "head"]
    missing_fields = [field for field in required_fields if not getattr(review_request, field, None)]
    if missing_fields:
        raise HTTPException(
            status_code=400, 
            detail=f"Missing required fields: {', '.join(missing_fields)}"
        )
    
    # Get GitHub token (from payload or environment variable)
    try:
        github_token = review_request.get_github_token()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Prepare payload for Celery task
    payload_dict = review_request.dict(exclude_none=True)
    payload_dict["github_token"] = github_token  # Ensure token is included
    
    # Dispatch task to Celery
    try:
        task = review_code_worker.apply_async(
            args=[payload_dict],
            queue=QueueConstants.CODE_REVIEW_QUEUE
        )
        logger.info(f"Code review task dispatched with task ID: {task.id}")
        
        return {
            "status": "success",
            "message": "Code review request submitted to Celery worker.",
            "task_id": task.id
        }
    except Exception as e:
        logger.error(f"Failed to dispatch Celery task: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to dispatch task: {str(e)}")