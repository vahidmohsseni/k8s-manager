import asyncio
import time
import zmq
from zmq.asyncio import Context
import logging
from typing import List

from server import Server
from task import Task


FORMAT = '%(asctime)s %(levelname)s %(message)s'
logging.basicConfig(#filename="backend-service.log",
                    format=FORMAT,
                    level=logging.DEBUG)


QUEUE_MAX_SIZE = 20

context = Context.instance()


def get_tasks(args):
    return {"status": "ok", "tasks": [task.name for task in server.tasks_list]}


def create_task(args):
    """args order: task_name, task_args, task_return_type"""
    task = Task(args[0], args[1], args[2])
    server.tasks_list.append(task)
    return {"status": "ok"}


async def stop_task(args):
    return await server.stop_task(args[0])


async def delete_task(args):
    return await server.delete_task(args[0])


def default_response(args):
    return {"status": "not applicable"}


async def ping() -> None:
    """print dots to indicate idleness"""
    while True:
        await asyncio.sleep(0.5)
        # logging.info(".")


async def api_call() -> None:
    PROCESS_MAPS = {"GET-TASKS": (get_tasks, None),
                    "DEFAULT": (default_response, None),
                    "CREATE-TASK": (create_task, None),
                    "STOP-TASK": (stop_task, "async"),
                    "DELETE-TASK": (delete_task, "async"),
                    }
    reply = context.socket(zmq.REP)
    # TODO: read the socket address from arguments
    reply.bind("tcp://*:5555")
    while True:
        req = await reply.recv_json()
        logging.info(f"received request: {req}")
        if not isinstance(req, dict):
            continue
        
        cmd = req.get("cmd", "DEFAULT")
        args = req.get("args", None)
        reply.send_json(
            PROCESS_MAPS[cmd][0](args)
            if PROCESS_MAPS[cmd][1] is None 
            else await PROCESS_MAPS[cmd][0](args)
            )


async def node_controller() -> None:
    pass



if __name__ == "__main__":
    logging.info("Strating the service")
    server = Server()

    asyncio.run(
        asyncio.wait(
            [
                ping(),
                api_call(),
                server.run(),
                server.control(),
                server.task_manager(),
                node_controller()
            ]
        )
    )