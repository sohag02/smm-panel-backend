from fastapi import FastAPI, BackgroundTasks, HTTPException
from models import FacebookConfig, YoutubeConfig
from services import load_services
from utils import run_script_async, load_scripts, update_config_file
from configparser import ConfigParser
from db import add_service, get_services, update_order_status
import queue
from typing import TypedDict
from pydantic import BaseModel
from models import OrderStatus
import os

from task import handle_task
from queue_config import task_queue
from rq.job import Job
from rq.registry import StartedJobRegistry, FinishedJobRegistry, FailedJobRegistry

from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Task(BaseModel):
    order_id: int
    service_name: str
    service_id: int
    required_config: FacebookConfig | YoutubeConfig


@app.get("/")
async def root():
    return {"message": "Hello World"}

def refresh_services():
    services = load_services()
    db_services = get_services()
    service_names = [service["name"] for service in db_services]

    if len(services) != len(service_names):
        for service in services:
            if service not in service_names:
                add_service(service)


@app.get("/reload-services/")
async def reload_services(background_tasks: BackgroundTasks):
    background_tasks.add_task(refresh_services)
    return {"message": "Services Reloaded"}

    
@app.post("/service/{service_name}/")
def service(service_name:str, task : Task):
    update_order_status(task.order_id, OrderStatus.PROCESSING.value)

    return {'message':service_name}

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "services")

@app.get("/config/{script_name}")
def get_script_config(script_name: str):
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    config_file = os.path.join(script_path, "config.ini")

    if not os.path.isfile(config_file):
        raise HTTPException(status_code=404, detail="Config file not found")

    # Parse the config.ini file
    config = ConfigParser()
    config.read(config_file)

    # Convert config to a dictionary format
    config_dict = {section: dict(config.items(section)) for section in config.sections()}

    return config_dict

@app.post('/run/{script}')
def run_script(script: str, data: dict):
    print(data)
    order_id = str(data.get("order_id"))
    # Enqueue the task
    job = task_queue.enqueue(
        'task.handle_task',
        args=[script, data],
        job_id=order_id
    )
    return {
        'message': 'run successful',
        'script': script,
        'task_id': job.id
    }

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    try:
        job = Job.fetch(task_id, connection=task_queue.connection)
        status = job.get_status()
        
        if status == 'finished':
            return {"status": status, "result": job.result, "position": 0}
        elif status == 'failed':
            return {"status": status, "error": str(job.exc_info), "position": 0}
        else:
            position = get_queue_position(task_id)
            return {"status": status, "position": position}
    except Exception as e:
        return {"status": "not_found", "error": str(e)}

def get_queue_position(task_id: str):
    # Get all jobs in the queue
    queue_jobs = task_queue.get_jobs()
    for index, job in enumerate(queue_jobs):
        if job.id == task_id:
            return index + 1
    return 0  # Job might be running or completed

@app.post('/edit/{script}')
def edit_script(script:str, data: dict):
    print(data)
    update_config_file(script, data)
    return {
        'message': 'edit sucessful',
        'script': script
    }

@app.get("/scripts/")
def scripts():
    return {'scripts': load_scripts()}