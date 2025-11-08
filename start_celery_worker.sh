celery -A app.celery_app worker \
    --loglevel=info \
    --queues=code_review_queue,github_comment_queue \
    --concurrency=2

