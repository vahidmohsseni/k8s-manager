import asyncio

class Connection:
    def __init__(self, reader, writer) -> None:
        self.reader: asyncio.StreamReader = reader
        self.writer: asyncio.StreamWriter = writer

    async def handler(self):
        pass
    
    async def send(self, data):
        self.writer.write(data)
        await self.writer.drain()
    
    async def recv(self, n=1024):
        return await self.reader.read(n)
    

class Server:
    def __init__(self) -> None:
        self.connections = []

    async def run(self) -> None:
        # TODO: read the address from args 
        socket = await asyncio.start_server(self.handle_connection, "0.0.0.0", 5556)
        async with socket: 
            await socket.serve_forever()

    async def handle_connection(self, reader, writer):
        connection = Connection(reader, writer)
        