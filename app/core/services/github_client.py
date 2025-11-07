import os
import httpx
import logging
import requests
from typing import Optional, Tuple

from fastapi import HTTPException

GITHUB_API = "https://api.github.com"
GITHUB_BOT_TOKEN = os.getenv("GITHUB_BOT_TOKEN")


logger = logging.getLogger(__name__)


def get_pr_refs(owner: str, repo: str, pr_number: int, token: str) -> Tuple[str, str]:
    """Fetches base and head refs from a GitHub PR.

    """
    if not token:
        raise HTTPException(status_code=401, detail="GitHub token is required")
    
    url = f"{GITHUB_API}/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"token {token}"
    }
    # TODO FUNKY exception handling and retries
    resp = requests.get(url, headers=headers, timeout=15)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=f"Failed to get PR info: {resp.text}")

    try:
        pr_data = resp.json()
        base_ref = pr_data["base"]["ref"]
        head_ref = pr_data["head"]["ref"]
        return base_ref, head_ref
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Invalid JSON from GitHub: {resp.text[:200]} ({str(e)})")


def get_diff_from_github(owner: str, repo: str, base: str, head: str, max_bytes: int = 500, token: str = "") -> Tuple[str, bool]:
    """
    Fetch diff from GitHub compare endpoint and return (diff_text, truncated).
    """
    if not token:
        raise HTTPException(status_code=401, detail="GitHub token is required")
    
    url = f"{GITHUB_API}/repos/{owner}/{repo}/compare/{base}...{head}"
    headers = {
        "Accept": "application/vnd.github.v3.diff",
        "Authorization": f"token {token}"
    }
    # TODO FUNKY exception handling and retries
    resp = requests.get(url, headers=headers, stream=True, timeout=60)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=f"GitHub compare failed: {resp.text}")

    content = bytearray()
    for chunk in resp.iter_content(chunk_size=16384):
        if not chunk:
            break
        content.extend(chunk)
        if len(content) > max_bytes:
            break

    truncated = len(content) > max_bytes
    return bytes(content[:max_bytes]).decode("utf-8", errors="replace"), truncated


async def post_comment_to_github(payload, token: Optional[str] = None):
    """
    Post a comment to a GitHub PR.
    """
    repo = payload.get("repo")
    pr_number = payload.get("pr_number")
    review_result = payload.get("review_result")
    
    token = payload.get("github_token")

    if not token:
        raise HTTPException(
            status_code=401,
            detail="GitHub token is required. Provide github_token in payload."
        )

    comment_body = f"{review_result}"
    url = f"{GITHUB_API}/repos/{repo}/issues/{pr_number}/comments"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"token {token}"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json={"body": comment_body})
        if response.status_code != 201:
            raise HTTPException(status_code=response.status_code, detail=f"Failed to post comment: {response.text}")
    logger.info(f"Comment Posted repo:{repo} - Pr Number: {pr_number}")
