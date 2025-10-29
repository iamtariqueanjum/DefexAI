import os
import requests
from fastapi import APIRouter, HTTPException

from app.core.ai_agent import analyze_code_diff
from .models import ReviewRequest

router = APIRouter()

GITHUB_API = "https://api.github.com"


def gh_headers():
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github.v3.diff"}
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


def get_pr_refs(owner: str, repo: str, pr_number: int):
    """Get base/head refs for a PR"""
    url = f"{GITHUB_API}/repos/{owner}/{repo}/pulls/{pr_number}"
    
    resp = requests.get(url, headers=gh_headers(), timeout=15)
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Failed to get PR info: {resp.text}")
    pr = resp.json()
    return pr["base"]["ref"], pr["head"]["ref"]



def get_diff_from_github(owner: str, repo: str, base: str, head: str, max_bytes: int = 500):
    """Fetch diff from GitHub compare endpoint"""
    url = f"{GITHUB_API}/repos/{owner}/{repo}/compare/{base}...{head}"
    headers = gh_headers()
    headers["Accept"] = "application/vnd.github.v3.diff"

    resp = requests.get(url, headers=headers, stream=True, timeout=60)
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"GitHub compare failed: {resp.text}")

    content = b""
    for chunk in resp.iter_content(chunk_size=16384):
        content += chunk
        if len(content) > max_bytes:
            break

    truncated = len(content) > max_bytes
    return content[:max_bytes].decode("utf-8", errors="replace"), truncated



@router.post("/code/review")
async def review_code(payload: ReviewRequest):
    diff_text = payload.diff
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
