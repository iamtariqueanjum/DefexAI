from fastapi import FastAPI, Request
from app.core.routers import code_reviewer

app = FastAPI(title="DefexAI Code Reviewer")
app.include_router(code_reviewer.router)