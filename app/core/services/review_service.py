from fastapi import HTTPException

import logging
import os

from app.core.models.models import ReviewRequest
from app.core.services.github_client import get_pr_refs, get_diff_from_github
from app.core.services.open_ai_agent import analyze_code_diff


logger = logging.getLogger(__name__)


async def review_code(payload):
    if isinstance(payload, ReviewRequest):
        payload_dict = payload.dict()
    else:
        payload_dict = payload
    
    if not payload_dict.get('github_token'):
        raise HTTPException(status_code=401, detail="github_token is required")
    
    diff_text = payload_dict.get('diff')
    try:
        # TODO remove FUNKY 
        logger.info("FUNKY review_code payload: %s", payload_dict)
    except Exception:
        # Fallback to repr() if dict() isn't available for some reason
        logger.info("review_code payload (repr): %s", repr(payload_dict))
    if not diff_text:
        if not payload_dict.get('repo'):
            raise HTTPException(status_code=400, detail="Either diff or repo info must be provided")

        if "/" not in payload_dict.get('repo'):
            raise HTTPException(status_code=400, detail="repo must be 'owner/repo'")

        owner, repo = payload_dict.get('repo').split("/", 1)

        base = payload_dict.get('base')
        head = payload_dict.get('head')
        token = payload_dict.get('github_token')
        
        if payload_dict.get('pr_number'):
            try:
                
                base, head = get_pr_refs(owner, repo, payload_dict.get('pr_number'), token=token)
                # TODO remove FUNKY 
                logger.info("FUNKY Fetched PR refs for %s/%s PR %s: %s...%s", owner, repo, payload_dict.get('pr_number'), base, head)
            except Exception:
                logger.exception("Failed to fetch PR refs for %s/%s PR %s", owner, repo, payload_dict.get('pr_number'))
                raise

        if not base or not head:
            raise HTTPException(status_code=400, detail="Provide either diff or base/head or pr_number")

        try:
            diff_text, truncated = get_diff_from_github(owner, repo, base, head, payload_dict.get('max_bytes'), token=token)
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
        review_markdown = analyze_code_diff(diff_text)
    except Exception as e:
        # Log stack trace for server-side debugging, then return a controlled 500 to client
        logger.exception("AI analysis failed")
        raise HTTPException(status_code=500, detail=f"AI code review failed: {e}")

    return {
        "truncated": truncated,
        "review": review_markdown
    }