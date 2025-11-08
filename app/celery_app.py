import os
import logging
from celery import Celery
from kombu import Queue
from app.core.utils.constants import QueueConstants

logger = logging.getLogger(__name__)

# Celery broker configuration: prefer CELERY_BROKER_URL, fallback to RABBITMQ_URL, otherwise localhost
broker_url = os.getenv("CELERY_BROKER_URL") or os.getenv("RABBITMQ_URL") or "amqp://guest:guest@localhost//"

app = Celery("defexai", broker=broker_url)

# Celery configuration
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    # Configure task routes to use specific queues
    task_routes={
        "defexai.review_code_worker": {"queue": QueueConstants.CODE_REVIEW_QUEUE},
        "defexai.post_comment_worker": {"queue": QueueConstants.GITHUB_COMMENT_QUEUE},
    },
    # Define queues
    task_queues=(
        Queue(QueueConstants.CODE_REVIEW_QUEUE, routing_key=QueueConstants.CODE_REVIEW_QUEUE),
        Queue(QueueConstants.GITHUB_COMMENT_QUEUE, routing_key=QueueConstants.GITHUB_COMMENT_QUEUE),
    ),
)

# Explicitly import tasks to ensure they're registered
# This must happen AFTER app configuration
from app.workers import review_worker, comment_worker  # noqa: E402

# Also use autodiscover as backup
app.autodiscover_tasks(["app.workers"])


