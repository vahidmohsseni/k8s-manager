import asyncio

class Connection():
    def __init__(self, address = "localhost", port = 5556) -> None:
        self._address = address
        self._port = port
        self.reader: asyncio.StreamReader = None
        self.writer: asyncio.StreamWriter = None

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self._address, self._port)
        asyncio.run(self.connection)

    async def send(self, data):
        self.connection.writer.write(data)
        await self.connection.writer.drain()
    
    async def recv(self, n=1024):
        return await self.connection.reader.read(n)
