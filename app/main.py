from fastapi import FastAPI
import logging
import sys

from app.core.routers.code_reviewer import router

# Configure logging so that module loggers (like app.core.routers.code_reviewer)
# emit INFO+ messages to stdout. GitHub Actions captures stdout/stderr, so
# this makes the `logger.info(...)` calls visible in workflow logs.
logging.basicConfig(
	stream=sys.stdout,
	level=logging.INFO,
	format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

app = FastAPI(title="DefexAI Code Reviewer")
app.include_router(router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "App is running healthy!"}
