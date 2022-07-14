import asyncio
import time
import zmq
from zmq.asyncio import Context
import logging

from server import Server

FORMAT = '%(asctime)s %(levelname)s %(message)s'
logging.basicConfig(#filename="backend-service.log",
                    format=FORMAT,
                    level=logging.DEBUG)

context = Context.instance()

def get_tasks(*args):
    return {"status": "ok", "tasks": []}


def create_task(*args):
    return {"status": "ok"}


def default_response(*args):
    return {"status": "not applicable"}


async def ping() -> None:
    """print dots to indicate idleness"""
    while True:
        await asyncio.sleep(0.5)
        # logging.info(".")


async def api_call() -> None:
    PROCESS_MAPS = {"GET-TASKS": get_tasks,
                    "DEFAULT": default_response,
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
        
        reply.send_json(PROCESS_MAPS[cmd](args))


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
                node_controller()
            ]
        )
    )