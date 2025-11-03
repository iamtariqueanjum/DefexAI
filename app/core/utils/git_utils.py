import os
import requests
from typing import Optional, Tuple

from fastapi import HTTPException

GITHUB_API = "https://api.github.com"


def get_pr_refs(owner: str, repo: str, pr_number: int, token: Optional[str] = None) -> Tuple[str, str]:
    """Fetches base and head refs from a GitHub PR.

    This function requires an explicit token to be passed. It returns a
    (base_ref, head_ref) tuple. On error it raises an HTTPException with a
    helpful status and message.
    """
    url = f"{GITHUB_API}/repos/{owner}/{repo}/pulls/{pr_number}"
    use_token = token or os.getenv("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json"}
    if use_token:
        headers["Authorization"] = f"token {use_token}"

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


def get_diff_from_github(owner: str, repo: str, base: str, head: str, max_bytes: int = 500, token: Optional[str] = None) -> Tuple[str, bool]:
    """Fetch diff from GitHub compare endpoint and return (diff_text, truncated).

    If `token` is provided it will be used for Authorization; otherwise the
    request is unauthenticated (which may hit rate limits).
    """
    url = f"{GITHUB_API}/repos/{owner}/{repo}/compare/{base}...{head}"
    headers = {"Accept": "application/vnd.github.v3.diff"}
    if token:
        headers["Authorization"] = f"token {token}"

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

