import asyncio
import time
import logging
import json

from task import Task


class Connection:

    def __init__(self, reader, writer, name) -> None:
        self.reader: asyncio.StreamReader = reader
        self.writer: asyncio.StreamWriter = writer
        self.last_heartbeat: float = time.time()
        self.name = name
        self.info = None
        self.status = "ready" # ready, busy, offline
        self.task: Task = None
    
    async def set_task(self, task: Task):
        self.task = task
        payload = {
            "task_name": task.name,
            "args_to_run": task.args_to_run,
            "return_type": task.return_type,
        }
        await self.send("task", payload)
        self.status = "busy"
        # update task status
        self.task.change_status("scheduled")
        self.task.set_assigned_node(self.name)

    async def stop_task(self):
        # SUGGESTION:
        # we can check the task name here and make sure they are same
        await self.send("stop-task")
    
    def unset_task(self):
        self.task = None
        self.status = "ready"

    async def handler(self):
        break_flag = False
        while not break_flag:
            data_generator = self.recv()
            async for data in data_generator:
                if data[0] == "":
                    break_flag = True
                    break
                elif data[0] == "ping":
                    self.last_heartbeat = time.time()
                    await self.send("pong")
                elif data[0] == "info":
                    self.info = data[3]
                    logging.debug(f"{self.name} received info: {self.info}")
                elif data[0] == "task-running":
                    logging.debug(f"{self.name} node is running task: {data[3]}")
                    self.task.change_status("running")
                elif data[0] == "task-finished":
                    logging.debug(f"{self.name} node finished task: {data[3]}")
                    self.task.change_status("finished", data[3]["return_value"])
                    self.unset_task()
                elif data[0] == "task-failed":
                    logging.debug(f"{self.name} node failed task: {data[3]}")
                    self.task.change_status("failed", data[3]["return_value"])
                    self.unset_task()
                elif data[0] == "task-stopped":
                    logging.debug(f"{self.name} node stopped task: {data[3]}")
                    self.task.change_status("stopped")
                    self.unset_task()
                else:
                    print("not implemented for: ", data)
    
    @classmethod
    def serialize(cls, header: str, payload):
        """
        Serialize the payload into a bytes object
        0 to 15 bytes for the header
        16 to 20 bytes for the payload length
        21 to 24 bytes for the payload type -> str, json, file, list
        25 to end bytes for the payload
        Example:
            header: "info"
            payload: {"cpu": "50%", "memory": "50%"}
            data = b'info\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1fjson{"cpu": "50%", "memory": "50%"}'
        """
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
        Deserialize the data into a tuple of:
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
        Seperate multibyte data indicating with their index
        """
        start_index = 0
        sep = 0
        while True:
            payload_length = int.from_bytes(data[start_index + 16:start_index + 21], "big")
            if payload_length == 0:
                sep += 21
            else:
                sep += 25 + payload_length
            yield start_index, sep 
            start_index = sep
            if sep + 1 > len(data):
                break
    
    async def send(self, header, payload = None):
        # TODO: missing mechanism for data larger than 1024 bytes
        data = self.serialize(header, payload)
        await self._send(data)

    async def recv(self):
        data = await self._recv()
        for (start_index, sep) in self.seperator(data):
            header, payload_length, payload_type, payload = self.deserialize(data[start_index:sep])
            yield header, payload_length, payload_type, payload

    async def _send(self, data):
        self.writer.write(data)
        await self.writer.drain()
    
    async def _recv(self, n=1024):
        return await self.reader.read(n)
    