import asyncio
import time
import psutil

from client import Connection


async def send_status(socket: Connection) -> None:
    # get some information about the system
    # such as cpu usage, memory usage, etc.
    # send info to server
    await asyncio.sleep(2)
    while True:
        cpu_usage =  psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        await socket.send("status", {"cpu": cpu_usage, "memory": memory_usage}) 
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
        if data[0] == "pong":
            socket.last_heartbeat = time.time()
        else:
            print(data)
    

if __name__ == "__main__":
    socket = Connection()
    asyncio.run(
        asyncio.wait(
            [
                socket.connect(),
                heartbeat(socket),
                handler(socket),
                send_status(socket)

            ]
        )
    )
