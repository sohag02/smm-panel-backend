import logging
from models import OrderStatus
from utils import update_config_file
from db import update_order_status, refund_order
import subprocess
import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.results import Results
import dotenv
import os
import redis

dotenv.load_dotenv()

REDIS_ENDPOINT = os.environ.get("REDIS_ENDPOINT")
REDIS_PASSWORD = os.environ.get("UPSTASH_REDIS_PASSWORD")
REDIS_PORT = os.environ.get("UPSTASH_REDIS_PORT")   

# redis_url = f"rediss://:{REDIS_PASSWORD}@{REDIS_ENDPOINT}:{REDIS_PORT}"
redis_url = 'redis://212.47.68.148:6379'
print(f"Redis URL: {redis_url}")

# Setup Redis broker with results
redis_broker = RedisBroker(url=redis_url)
# redis_client = redis.StrictRedis(
#     host=REDIS_ENDPOINT,
#     port=REDIS_PORT,
#     password=REDIS_PASSWORD,
#     ssl=True,
# )
redis_client = redis.StrictRedis(
    host='212.47.68.148',
    port=6379
)

# Adding Results middleware for tracking results and status
redis_broker.add_middleware(Results(backend=redis_client))
dramatiq.set_broker(redis_broker)

logger = logging.getLogger(__name__)

def run_script(script_path):
    # Change to the directory of the script
    script_dir = os.path.dirname(script_path)
    os.chdir(script_dir)  # Change the current working directory to the script's directory
    cmd = f"python {os.path.basename(script_path)}"  # Run the script by its base name
    process = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f"Error running script: {stderr.decode().strip()}")
    return stdout.decode().strip()

@dramatiq.actor
def handle_task(script: str, data: dict):
    try:
        print("Processing task")
        logger.info(f"Processing task for script: {script}")
        order_id = data.get("order_id")
        data.pop("order_id", None)
        update_config_file(script, data)
        update_order_status(order_id, OrderStatus.PROCESSING.value)
        process = run_script(f'services/{script}/main.py')
        print("process", process)
        update_order_status(order_id, OrderStatus.COMPLETED.value)
        return {'message': 'successful', 'script': script, 'order_id': order_id}
    except Exception as e:
        print(e)
        update_order_status(order_id, OrderStatus.FAILED.value)
        refund_order(order_id)
        logger.error(f"Error processing task: {e}")
        return {'message': 'error', 'script': script, 'order_id': order_id, 'error': str(e)}

# Run worker: rq worker task_queue