import asyncio
import time

import zmq
from zmq.asyncio import Context

context = Context.instance()

async def ping() -> None:
    """print dots to indicate idleness"""
    while True:
        await asyncio.sleep(0.5)
        # logging.info(".")


async def contact() -> None:
    socket = context.socket(zmq.CLIENT)
    
    socket.connect("tcp://localhost:5556")

    while True:
        socket.send(b'1234')
        response = await socket.recv()
        print(f"from server: {response}")
        response = socket.recv()
        print(f"from server: {response}")
        time.sleep(1)
    

if __name__ == "__main__":
    asyncio.run(
        asyncio.wait(
            [
                ping(),
                contact()                
            ]
        )
    )