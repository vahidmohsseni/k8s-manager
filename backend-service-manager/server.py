import time
import asyncio

class Connection:
    def __init__(self, reader, writer, name) -> None:
        self.reader: asyncio.StreamReader = reader
        self.writer: asyncio.StreamWriter = writer
        self.last_heartbeat: float = time.time()
        self.name = name

    async def handler(self):
        while True:
            data = await self.recv()
            if data == b"":
                break
            elif data == b"ping":
                self.last_heartbeat = time.time()
                await self.send(b"pong")
            else:
                print(data)
    
    async def send(self, data):
        self.writer.write(data)
        await self.writer.drain()
    
    async def recv(self, n=1024):
        return await self.reader.read(n)
    

class Server:
    def __init__(self) -> None:
        self._address = "0.0.0.0"
        self._port = 5556
        self.connections = []
        self.counter = 1

    async def run(self) -> None:
        socket = await asyncio.start_server(self.handle_connection, self._address, self._port)
        async with socket: 
            await socket.serve_forever()

    async def handle_connection(self, reader, writer):
        name = f"client {self.counter}"
        connection = Connection(reader, writer, name)
        self.connections.append(connection)
        self.counter += 1
        await connection.handler()

    async def control(self) -> None:
        # check if any connections are dead
        # if so, terminate it and remove it from the list
        while True:
            for connection in self.connections:
                if time.time() - connection.last_heartbeat > 10:
                    connection.writer.close()
                    print(f"connection {connection.name} is closed")
                    self.connections.remove(connection)
            await asyncio.sleep(1)
