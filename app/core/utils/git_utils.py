import os
import requests
from typing import Optional

from fastapi import HTTPException

GITHUB_API = "https://api.github.com"


def gh_headers(token: Optional[str] = None):
    """Return headers for GitHub API requests. If `token` is provided use it,
    otherwise fall back to the GITHUB_TOKEN environment variable."""
    env_token = os.getenv("GITHUB_TOKEN")
    use_token = token or env_token
    headers = {"Accept": "application/vnd.github.v3.diff"}
    if use_token:
        headers["Authorization"] = f"token {use_token}"
    return headers


def get_pr_refs(owner: str, repo: str, pr_number: int, token: Optional[str] = None):
    """Get base/head refs for a PR"""
    url = f"{GITHUB_API}/repos/{owner}/{repo}/pulls/{pr_number}"
    
    resp = requests.get(url, headers=gh_headers(token), timeout=15)
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Failed to get PR info: {resp.text}")
    pr = resp.json()
    return pr["base"]["ref"], pr["head"]["ref"]



def get_diff_from_github(owner: str, repo: str, base: str, head: str, max_bytes: int = 500, token: Optional[str] = None):
    """Fetch diff from GitHub compare endpoint"""
    url = f"{GITHUB_API}/repos/{owner}/{repo}/compare/{base}...{head}"
    headers = gh_headers(token)
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

