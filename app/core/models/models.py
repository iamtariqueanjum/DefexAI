from pydantic import BaseModel
from typing import Optional
import os


class ReviewRequest(BaseModel):
    diff: Optional[str] = None
    repo: Optional[str] = None        # "owner/repo"
    pr_number: Optional[int] = None
    base: Optional[str] = None
    head: Optional[str] = None
    max_bytes: int = 500
    github_token: Optional[str] = None  # Optional: Can be provided or use GITHUB_BOT_TOKEN env var
    
    def get_github_token(self) -> str:
        """Get GitHub token from payload or environment variable."""
        if self.github_token:
            return self.github_token
        token = os.getenv("GITHUB_BOT_TOKEN")
        if not token:
            raise ValueError("github_token is required. Provide it in payload or set GITHUB_BOT_TOKEN environment variable.")
        return token
    
    