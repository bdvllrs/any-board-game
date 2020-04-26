import asyncio
from random import randint


async def wait_for_messages(machine_event):
    """
    Simulates the websocket
    """
    while True:
        sleeping_time = randint(0, 5)
        print("Wait for", sleeping_time)
        await asyncio.sleep(sleeping_time)  # simulate waiting for message
        print("Message received!")
        machine_event.set()


async def execute_state_machine(machine_event):
    state = 0
    while True:
        await machine_event.wait()
        state += 1
        print("State is", state)
        machine_event.clear()


async def main():
    machine_event = asyncio.Event()
    wait_message_task = asyncio.create_task(wait_for_messages(machine_event))
    execute_machine_task = asyncio.create_task(execute_state_machine(machine_event))

    await asyncio.gather(execute_machine_task,
                         wait_message_task)


if __name__ == '__main__':
    asyncio.run(main())
