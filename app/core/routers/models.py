from pydantic import BaseModel
from typing import Optional


class ReviewRequest(BaseModel):
    diff: Optional[str] = None
    repo: Optional[str] = None        # "owner/repo"
    pr_number: Optional[int] = None
    base: Optional[str] = None
    head: Optional[str] = None
    max_bytes: int = 500
    