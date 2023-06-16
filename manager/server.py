import time
import asyncio
from typing import List
import logging

from connection import Connection
from task import Task


class Server:
    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 5556,
    ) -> None:
        self._address = host
        self._port = port
        self.connections: List[Connection] = []
        self.counter = 1
        self.tasks_list: List[Task] = []

    async def run(self) -> None:
        socket = await asyncio.start_server(
            self.handle_connection, self._address, self._port
        )
        async with socket:
            await socket.serve_forever()

    async def handle_connection(self, reader, writer):
        name = f"client {self.counter}"
        connection = Connection(reader, writer, name)
        self.connections.append(connection)
        self.counter += 1
        await connection.handler()

    async def control(self) -> None:
        # checks if any connections are dead
        # if so, terminates it and removes it from the list
        while True:
            for connection in self.connections:
                if time.time() - connection.last_heartbeat > 10:
                    connection.writer.close()
                    logging.warning(f"connection {connection.name} is closed")
                    self.connections.remove(connection)
            await asyncio.sleep(1)

    def _find_ready_node(self) -> int:
        """
        finds the first ready node in the list of connections
        returns the index of the node
        if no node is ready, returns -1
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

    async def stop_task(self, task_name):
        for task in self.tasks_list:
            if task.name == task_name:
                worker_name = task.assigned_to
                for connection in self.connections:
                    if connection.name == worker_name:
                        await connection.stop_task()
                        return {"status": "ok"}
        return {"status": "error", "message": "task not found"}

    async def delete_task(self, task_name):
        await self.stop_task(task_name)
        for task in self.tasks_list:
            if task.name == task_name:
                self.tasks_list.remove(task)
                return {"status": "ok"}
        return {"status": "error", "message": "task not found"}

    async def start_task(self, task_name):
        for task in self.tasks_list:
            if task.name == task_name:
                if task.status != "stopped":
                    message = (
                        "you can only start a stopped task, "
                        f"current status is {task.status}"
                    )
                    return {"status": "error", "message": message}
                await self.schedule_task(task)
                return {"status": "ok"}
        return {"status": "error", "message": "task not found"}

    def task_status(self, task_name):
        for task in self.tasks_list:
            if task.name == task_name:
                return {"status": "ok", "task_status": task.status}
        return {"status": "error", "message": "task not found"}
