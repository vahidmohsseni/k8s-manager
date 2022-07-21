import time
import json
import asyncio
from typing import List
import logging

from connection import Connection
from task import Task


class Server:
    
    def __init__(self) -> None:
        self._address = "0.0.0.0"
        self._port = 5556
        self.connections = []
        self.counter = 1
        self.tasks_list: List[Task] = []

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

    def _find_ready_node(self) -> int:
        """
        find the first ready node in the list of connections
        return the index of the node
        if no node is ready, return -1
        """
        for i, connection in enumerate(self.connections):
            if connection.status == "ready":
                return i
        return -1
        
    async def schedule_task(self, task: Task):
        """
        schedule a task to a node
        """
        # find the first ready node
        index = self._find_ready_node()
        if index == -1:
            return 
        # send the task to the node
        conn: Connection = self.connections[index]
        await conn.set_task(task)

    async def task_manager(self) -> None:
        while True:
            for task in self.tasks_list:
                if task.status == "created":
                    await self.schedule_task(task)
            await asyncio.sleep(1)
