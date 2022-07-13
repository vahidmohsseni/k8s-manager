import asyncio


class Connection():
    def __init__(self, address = "localhost", port = 5556) -> None:
        self._address = address
        self._port = port
        self.reader: asyncio.StreamReader = None
        self.writer: asyncio.StreamWriter = None
        self.last_heartbeat: float = None

    async def connect(self) -> None:
        self.reader, self.writer = await asyncio.open_connection(self._address, self._port)

    async def send(self, data):
        self.writer.write(data)
        await self.writer.drain()
    
    async def recv(self, n=1024):
        return await self.reader.read(n)
