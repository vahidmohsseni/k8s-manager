"""Example using zmq with asyncio coroutines"""
# Copyright (c) PyZMQ Developers.
# This example is in the public domain (CC-0)

import asyncio

import zmq
from zmq.asyncio import Context

url = "tcp://127.0.0.1:5555"

ctx = Context.instance()


async def ping() -> None:
    """print dots to indicate idleness"""
    while True:
        await asyncio.sleep(0.5)
        print(".")


async def receiver() -> None:
    """receive messages with polling"""
    req = ctx.socket(zmq.REQ)
    req.connect(url)
    # poller = Poller()
    # poller.register(req, zmq.POLLIN)
    while True:
        await asyncio.sleep(0.8)
        # events = await poller.pll()
        req.send_string("111$$@@111")
        # if req in dict(eveonts):

        msg = await req.recv_string()
        print("recvd", msg)


async def receiver2() -> None:
    """receive messages with polling"""
    req = ctx.socket(zmq.REQ)
    req.connect(url)
    # poller = Poller()
    # poller.register(req, zmq.POLLIN)
    while True:
        await asyncio.sleep(1)
        # events = await poller.pll()
        req.send_string("dasnd2222sjdsad")
        # if req in dict(eveonts):

        msg = await req.recv_string()
        print("recvd", msg)


async def sender() -> None:
    """send a message every second"""
    rep = ctx.socket(zmq.REP)
    rep.bind(url)
    while True:
        msg = await rep.recv_string()
        print(f"sender is receiving message: {msg}")
        rep.send_string(msg)
        # await asyncio.sleep(1)


asyncio.run(
    asyncio.wait(
        [
            ping(),
            receiver(),
            receiver2(),
            sender(),
        ]
    )
)
