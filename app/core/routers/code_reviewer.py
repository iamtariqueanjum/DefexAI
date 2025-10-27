from fastapi import APIRouter, Request

from app.core.ai_agent import analyze_code_diff

router = APIRouter()

@router.post("/code/review")
async def review_code(request: Request):
    payload = await request.json()
    diff = payload.get("diff", "")
    repo = payload.get("repo", "unknown-repo")

    if not diff:
        return {"error": "Diff not provided"}

    review_result = analyze_code_diff(diff)
    return {
        "repo": repo,
        "summary": review_result,
    }
