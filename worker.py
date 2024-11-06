from rq import Worker, Queue
from redis import Redis
from queue_config import redis_conn, task_queue
import pytz
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

TIMEZONE = 'Asia/Kolkata'

if __name__ == '__main__':
    logger.info("Starting worker...")
    logger.info(f"Connected to Redis: {redis_conn.ping()}")
    logger.info(f"Listening to queue: {task_queue.name}")

    while True:
        try:
            logger.info("Connecting to Redis...")
            worker = Worker(
                [task_queue],
                connection=redis_conn,
                # worker_timezone=pytz.timezone(TIMEZONE)
                # is_async=False
            )
            logger.info("Worker started, waiting for tasks...")
            worker.work()
        except Exception:
            logger.error("Error connecting to Redis")

