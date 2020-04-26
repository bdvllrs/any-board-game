import asyncio


class Event:
    def __init__(self):
        self.semaphore = asyncio.Semaphore(0)

    async def wait(self):
        await self.semaphore.acquire()

    def trigger(self):
        self.semaphore.release()
