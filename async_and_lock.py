import asyncio
from threading import Lock, Thread
import time
from typing import List

class Task:
    def __init__(self, name) -> None:
        self.lock = Lock()
        self.counter = 1
        self.id = name

tasks_list: List[Task] = []


async def add_task():
    c = 1
    while c < 100:
        tasks_list.append(Task(c))
        c += 1
        await asyncio.sleep(0.01)


async def edit_task() -> None:
    c = 1
    while True:
        for t in tasks_list:
            #with t.lock:
                t.counter += 1
                
                print("task id:", t.id, "counter", t.counter)

        await asyncio.sleep(0.001)
    

def delete_task() -> None:
    c = 1
    while True:
        for t in tasks_list:
           # with t.lock:
                if t.counter > 6:
                    tasks_list.remove(t)
                    print("task deleted", t.id, t.counter)

        time.sleep(0.1)


if __name__ == "__main__":
    t = Thread(target=delete_task, args=())
    t.start()
    asyncio.run(
        asyncio.wait(
            [
                add_task(),
                edit_task(),
                #delete_task(),
            ]
        )
    )