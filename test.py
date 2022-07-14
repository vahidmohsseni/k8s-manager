import asyncio


async def kir1() -> None:
    c = 1
    while 1:
        print(1)
        await asyncio.sleep(1)
        c += 1
        if c >=3:
            return 


async def kir2() -> None:
    while 1:
        print(2)
        await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(kir1())
    print("dskda")
    asyncio.run(kir2())


