import asyncio
import time

import aiohttp
from aiohttp import web

states = dict()


class Event:
    def __init__(self):
        self.semaphore = asyncio.Semaphore(0)

    async def wait(self):
        await self.semaphore.acquire()

    def trigger(self):
        self.semaphore.release()


async def execute_state_machine(state, event):
    while True:
        await event.wait()
        state += 1
        print(state)


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    event = Event()
    states[ws] = 0
    asyncio.create_task(execute_state_machine(states[ws], event))

    print('websocket connection opened')
    print(request.path)
    print(request.query)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            print("message received,", msg.data)
            if msg.data == 'close':
                await ws.close()
            else:
                event.trigger()

        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' %
                  ws.exception())

    print('websocket connection closed')

    return ws


app = web.Application()
app.add_routes([web.get('/{round_id}', websocket_handler)])

if __name__ == '__main__':
    web.run_app(app)
