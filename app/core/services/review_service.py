from fastapi import HTTPException

import logging
import os

from app.core.models.models import ReviewRequest
from app.core.services.github_client import get_pr_refs, get_diff_from_github
from app.core.services.open_ai_agent import analyze_code_diff


logger = logging.getLogger(__name__)


async def review_code(payload: ReviewRequest):
    diff_text = payload.get('diff')
    # Log the incoming payload for debugging / auditing
    try:
        # Use dict() so Pydantic model data is serialized; avoid heavy prints
        # TODO remove FUNKY 
        logger.info("FUNKY review_code payload: %s", payload.dict())
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
            try:
                token = os.getenv("GITHUB_TOKEN")
                base, head = get_pr_refs(owner, repo, payload.pr_number, token=token)
                # TODO remove FUNKY 
                logger.info("FUNKY Fetched PR refs for %s/%s PR %s: %s...%s", owner, repo, payload.pr_number, base, head)
            except Exception:
                logger.exception("Failed to fetch PR refs for %s/%s PR %s", owner, repo, payload.pr_number)
                raise

        if not base or not head:
            raise HTTPException(status_code=400, detail="Provide either diff or base/head or pr_number")

        try:
            token = os.getenv("GITHUB_TOKEN")
            diff_text, truncated = get_diff_from_github(owner, repo, base, head, payload.max_bytes, token=token)
            # TODO remove FUNKY 
            logger.info("FUNKY Fetched diff for %s/%s %s...%s (truncated=%s) ", owner, repo, base, head, truncated)
            # TODO remove FUNKY 
            logger.info("FUNKY Diff content : %s", diff_text)
        except Exception:
            logger.exception("Failed to fetch diff for %s/%s %s...%s", owner, repo, base, head)
            raise
    else:
        truncated = False

    if not diff_text.strip():
        raise HTTPException(status_code=400, detail="Empty diff (no changes found)")
    try:
        review_issues = analyze_code_diff(diff_text)
    except Exception as e:
        # Log stack trace for server-side debugging, then return a controlled 500 to client
        logger.exception("AI analysis failed")
        raise HTTPException(status_code=500, detail=f"AI code review failed: {e}")

    return {
        "truncated": truncated,
        "issues": review_issues
    }