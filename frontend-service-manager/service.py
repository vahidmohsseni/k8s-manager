import asyncio
import time
import psutil
import logging
import subprocess
import os

from client import Connection


FORMAT = '%(asctime)s %(levelname)s %(message)s'
logging.basicConfig(#filename="backend-service.log",
                    format=FORMAT,
                    level=logging.DEBUG)


def download_task(task_name):
    """
    Download the task from the server
    """
    base_address = "http://localhost:5001/api/v1"
    url = base_address + "/tasks/" + task_name + "/download"
    
    # create a directory to store the task tag it with the timestamp
    task_dir = os.curdir + "/.tasks/" + task_name + "-" + str(int(time.time()))
    os.makedirs(task_dir, exist_ok=True)

    process = subprocess.run(
            [    
                "curl",
                url, 
                "-JO", 
                "-w \"%{http_code}\""
            ],
            capture_output=True,
            cwd=task_dir
        )
    if process.returncode != 0:
        logging.error(f"error downloading task: {task_name}", process.stderr)
        return 0

    if "200" not in process.stdout.decode():
        logging.error(f"task: {task_name} not found, return code:", process.stdout)
        return 0

    return 1


async def run_task(socket: Connection, task_name, task_args, return_type) -> None:
    """
    Run the task
    """
    if not download_task(task_name):
        return

    logging.info(f"running task: {task_name}")
    task_dir = [dir
        for dir in os.listdir(os.getcwd() + "/.tasks/") if (task_name in dir and "venv" != dir)
        ]
    task_dir.sort()
    task_dir = os.getcwd() + "/.tasks/" + task_dir[-1]
    python_dir = os.getcwd() + "/.tasks/" + "venv/bin"
    task_args = task_args.split(" ")
    try:
        process: asyncio.subprocess.Process = await asyncio.subprocess.create_subprocess_exec(
            
            python_dir + "/python", 
            *task_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd = task_dir
        )
        
        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            logging.info(f"task: {task_name} completed with return code: {process.returncode}")
            await socket.send("task-finished", {"task_name": task_name, "return_value": stdout.decode()})
        else:
            logging.error(f"task: {task_name} failed with return code: {process.returncode}")
            await socket.send("task-failed", {"task_name": task_name, "return_value": stderr.decode()})

    except Exception as e:
        logging.error(f"error running task: {task_name}", e)


async def send_info(socket: Connection) -> None:
    # get some information about the system
    # such as cpu usage, memory usage, etc.
    # send info to server
    await asyncio.sleep(2)
    while True:
        cpu_usage =  psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        await socket.send("info", {"cpu": cpu_usage, "memory": memory_usage}) 
        await asyncio.sleep(60)
        

async def heartbeat(socket: Connection) -> None:
    await asyncio.sleep(1.6)
    # send heartbeat to server
    while True:
        await socket.send("ping")
        await asyncio.sleep(2)


async def handler(socket: Connection) -> None:
    await asyncio.sleep(2)
    while True:
        data = await socket.recv()
        if data[0] == "":
            # TODO: handle the case when the server is not available
            logging.error("connection closed!")
            exit(1)
        elif data[0] == "pong":
            socket.last_heartbeat = time.time()
        elif data[0] == "task":
            print(data)
            # create a task
            asyncio.create_task(
                run_task(socket, data[3]["task_name"], data[3]["args_to_run"], data[3]["return_type"])
                )
        else:
            print(data)


async def reconnect(socket: Connection) -> None:
    await asyncio.sleep(2)
    time_interval = 1
    while socket.reconnect:
        socket.reconnect = False
        logging.info("reconnecting...")
        try:
            await socket.connect()
        except Exception as e:
            print(e)
        await asyncio.sleep(time_interval)
        time_interval *= 2


def create_virtual_environment() -> None:
    """
    Run the init.sh to build the virtual environment
    """
    logging.info("creating virtual environment")
    subprocess.run(["bash", "init.sh"])
    logging.info("virtual environment created!")
    

if __name__ == "__main__":
    create_virtual_environment()
    socket = Connection()
    asyncio.run(
        asyncio.wait(
            [
                socket.connect(),
                heartbeat(socket),
                handler(socket),
                send_info(socket)
            ]
        )
    )
