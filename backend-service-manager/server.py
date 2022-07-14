import time
import json
import asyncio

class Connection:
    def __init__(self, reader, writer, name) -> None:
        self.reader: asyncio.StreamReader = reader
        self.writer: asyncio.StreamWriter = writer
        self.last_heartbeat: float = time.time()
        self.name = name
        self.status = None


    async def handler(self):
        while True:
            data = await self.recv()
            if data[0] == "":
                break
            elif data[0] == "ping":
                self.last_heartbeat = time.time()
                await self.send("pong")
            elif data[0] == "status":
                self.status = data[3]
                print(self.name, self.status)
            else:
                print(data)
    

    @classmethod
    def serialize(cls, header: str, payload):
        """
        Serialize the payload into a bytes object
        0 to 15 bytes for the header
        16 to 20 bytes for the payload length
        21 to 24 bytes for the payload type -> str, json, file
        25 to end bytes for the payload
        Example:
            header: "status"
            payload: {"cpu": "50%", "memory": "50%"}
            data = b'status\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1fjson{"cpu": "50%", "memory": "50%"}'
        """
        # reserve 20 byte for header
        data = header.encode()
        if len(data) > 16:
            raise ValueError("header is too long")
        data += b"\0" * (16 - len(data))
        # check if payload is None
        if payload is None:
            return data
        # reserve 4 byte for payload type
        if isinstance(payload, str):
            # reserve 4 byte for payload length
            payload = payload.encode()
            data += len(payload).to_bytes(5, "big")
            data += "str".encode() + "\0".encode()
            data += payload
        elif isinstance(payload, dict):
            payload = json.dumps(payload).encode()
            data += len(payload).to_bytes(5, "big")
            data += "json".encode()
            data += payload
        # TODO: File type should be added here
        # file type is not supported yet
        else:
            raise ValueError("payload type is not supported")
            
        return data
    

    @classmethod
    def deserialize(self, data):
        """
        Deserialize the data into a tuple of (header, payload)
        """
        header = data[:16].decode()
        header = header.rstrip("\x00")
        payload_length = int.from_bytes(data[16:21], "big")
        # check if payload size is zero
        if payload_length == 0:
            return header, None, None, None
        payload_type = data[21:25].decode().rstrip("\x00")
        if payload_type == "str":
            payload = data[25:].decode()
        elif payload_type == "json":
            payload = json.loads(data[25:].decode())
        else:
            raise ValueError("payload type is not supported")

        return header, payload_length, payload_type, payload

    async def send(self, header, payload = None):
        # TODO: missing mechanism for data larger than 1024 bytes
        data = self.serialize(header, payload)
        await self._send(data)
    

    async def recv(self):
        data = await self._recv()
        header, payload_length, payload_type, payload = self.deserialize(data)
        return header, payload_length, payload_type, payload


    async def _send(self, data):
        self.writer.write(data)
        await self.writer.drain()
    
    async def _recv(self, n=1024):
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
