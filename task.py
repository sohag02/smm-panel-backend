import logging
from models import OrderStatus
from utils import update_config_file
from db import update_order_status, refund_order
import subprocess

logger = logging.getLogger(__name__)

def run_script(script_path):
    cmd = f"python {script_path}"
    process = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f"Error running script: {stderr.decode().strip()}")
    return stdout.decode().strip()

def handle_task(script: str, data: dict):
    try:
        print("Processing task")
        logger.info(f"Processing task for script: {script}")
        order_id = data.get("order_id")
        data.pop("order_id", None)
        update_config_file(script, data)
        update_order_status(order_id, OrderStatus.PROCESSING.value)
        process = run_script(f'services/{script}/main.py')
        update_order_status(order_id, OrderStatus.COMPLETED.value)
    except Exception as e:
        update_order_status(order_id, OrderStatus.FAILED.value)
        refund_order(order_id)
        logger.error(f"Error processing task: {e}")
    return {'message': 'successful', 'script': script, 'order_id': order_id}

# Run worker: rq worker task_queue