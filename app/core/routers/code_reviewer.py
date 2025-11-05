
from fastapi import APIRouter, HTTPException
import logging
import os

from app.core.models.models import ReviewRequest
from app.core.rabbit_mq.publisher import publish_message
from app.core.utils.constants import QueueConstants


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/code/review")
async def analyze_code(payload: dict):
    payload = ReviewRequest(**payload)
    payload_dict = payload.dict()
    if not payload_dict:
        raise HTTPException(status_code=400, detail="Invalid payload")
    required_fields = ["repo", "pr_number", "base", "head"]
    for field in required_fields:
        if not payload_dict.get(field):
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
    await publish_message(QueueConstants.CODE_REVIEW_QUEUE, payload.dict())
    return {"status": "success", "message": "Code review request published to queue."}