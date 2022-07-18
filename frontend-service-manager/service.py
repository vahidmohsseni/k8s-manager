import asyncio
import time
import psutil
import logging

from client import Connection


FORMAT = '%(asctime)s %(levelname)s %(message)s'
logging.basicConfig(#filename="backend-service.log",
                    format=FORMAT,
                    level=logging.DEBUG)


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


if __name__ == "__main__":
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
