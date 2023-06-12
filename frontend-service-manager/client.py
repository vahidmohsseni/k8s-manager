import asyncio
import json


class Connection:
    def __init__(self, address="localhost", port=5556) -> None:
        self._address = address
        self._port = port
        self.reader: asyncio.StreamReader = None
        self.writer: asyncio.StreamWriter = None
        self.last_heartbeat: float = None
        self.reconnect = False

    async def connect(self) -> None:
        self.reader, self.writer = await asyncio.open_connection(
            self._address, self._port
        )

    @classmethod
    def serialize(cls, header: str, payload):
        """
        Serialize the payload into a bytes object
        0 to 15 bytes for the header
        16 to 20 bytes for the payload length
        21 to 24 bytes for the payload type -> str, json, file
        25 to end bytes for the payload
        Example:
            header: "info"
            payload: {"cpu": "50%", "memory": "50%"}
            data = b'info\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1fjson{"cpu": "50%", "memory": "50%"}'
        """  # ruff: noqa
        # reserve 20 byte for header
        data = header.encode()
        if len(data) > 16:
            raise ValueError("header is too long")
        data += b"\0" * (16 - len(data))
        # check if payload is None
        if payload is None:
            zero = 0
            data += zero.to_bytes(5, "big")
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
        elif isinstance(payload, list):
            payload = json.dumps(payload).encode()
            data += len(payload).to_bytes(5, "big")
            data += "list".encode()
            data += payload
        # TODO: File type should be added here
        # file type is not supported yet
        else:
            raise ValueError("payload type is not supported")

        return data

    @classmethod
    def deserialize(cls, data):
        """
        Deserializes the data into a tuple of:
            (header, payload_length, payload_type, payload)
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
        elif payload_type == "list":
            payload = json.loads(data[25:].decode())
        else:
            raise ValueError("payload type is not supported")

        return header, payload_length, payload_type, payload

    @classmethod
    def seperator(cls, data):
        """
        Seperates multibyte data indicating with their index
        """
        start_index = 0
        sep = 0
        while True:
            payload_length = int.from_bytes(
                data[start_index + 16 : start_index + 21], "big"
            )
            if payload_length == 0:
                sep += 21
            else:
                sep += 25 + payload_length
            yield start_index, sep
            start_index = sep
            if sep + 1 > len(data):
                break

    async def send(self, header, payload=None):
        # TODO: missing mechanism for data larger than 1024 bytes
        data = self.serialize(header, payload)
        await self._send(data)

    async def recv(self):
        data = await self._recv()
        for start_index, sep in self.seperator(data):
            header, payload_length, payload_type, payload = self.deserialize(
                data[start_index:sep]
            )
            yield header, payload_length, payload_type, payload

    async def _send(self, data):
        self.writer.write(data)
        await self.writer.drain()

    async def _recv(self, n=1024):
        return await self.reader.read(n)


if __name__ == "__main__":
    # TEST Example of serialize and deserialize
    header = "info"
    payload = {"cpu": "50%", "memory": "50%"}
    data = Connection.serialize(header, payload)
    print(data)
    header, payload_length, payload_type, payload = Connection.deserialize(data)
    print(header, payload_length, payload_type, payload)

    multi_data = b'task\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00Jjson{"task_name": "first", "args_to_run": "hello.py 6", "return_type": "None"}pong\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    multi_data += multi_data
    data = multi_data
    print(len(data))
    # print(data[:99])
    # print(data[99:99+21])
    # print(data[99+21:99+21+99])
    # print(data[99+21+99:99+21+99+21])

    for start_index, sep in Connection.seperator(data):
        print(Connection.deserialize(data[start_index:sep]))
