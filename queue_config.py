import redis
from rq import Queue
import os
import dotenv

dotenv.load_dotenv()
REDIS_ENDPOINT = os.environ.get("UPSTASH_REDIS_ENDPOINT")
REDIS_PASSWORD = os.environ.get("UPSTASH_REDIS_PASSWORD")
REDIS_PORT = os.environ.get("UPSTASH_REDIS_PORT")
print(REDIS_ENDPOINT)
print(REDIS_PASSWORD)
print(REDIS_PORT)

# Configure Redis connection
redis_conn = redis.Redis(
    host=REDIS_ENDPOINT,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    ssl=True
)


# redis_conn = redis.Redis(host='212.47.68.148', port=6379, db=0)
# redis_conn.ping()


# Create a queue instance
task_queue = Queue('task_queue', connection=redis_conn, is_async=False) 