
from fastapi import APIRouter, HTTPException
import logging

from app.core.ai_agent import analyze_code_diff
from .models import ReviewRequest
from ..utils.git_utils import get_pr_refs, get_diff_from_github


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/code/review")
async def review_code(payload: ReviewRequest):
    diff_text = payload.diff
    # Log the incoming payload for debugging / auditing
    try:
        # Use dict() so Pydantic model data is serialized; avoid heavy prints
        logger.info("review_code payload: %s", payload.dict())
    except Exception:
        # Fallback to repr() if dict() isn't available for some reason
        logger.info("review_code payload (repr): %s", repr(payload))
    if not diff_text:
        if not payload.repo:
            raise HTTPException(status_code=400, detail="Either diff or repo info must be provided")

        if "/" not in payload.repo:
            raise HTTPException(status_code=400, detail="repo must be 'owner/repo'")

        owner, repo = payload.repo.split("/", 1)

        base = payload.base
        head = payload.head

        if payload.pr_number:
            base, head = get_pr_refs(owner, repo, payload.pr_number)

        if not base or not head:
            raise HTTPException(status_code=400, detail="Provide either diff or base/head or pr_number")

        diff_text, truncated = get_diff_from_github(owner, repo, base, head, payload.max_bytes)
    else:
        truncated = False

    if not diff_text.strip():
        raise HTTPException(status_code=400, detail="Empty diff (no changes found)")
    try:
        ai_review = analyze_code_diff(diff_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI code review failed: {e}")

    return {
        "truncated": truncated,
        "review": ai_review
    }
