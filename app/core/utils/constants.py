import os 


class QueueConstants:
    CODE_REVIEW_QUEUE = "code_review_queue"
    GITHUB_COMMENT_QUEUE = "github_comment_queue"


# TODO FUNKY move to environment variables
class RabbitMQConstants:
    RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")