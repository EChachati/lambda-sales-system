
import json
import asyncio
#from websocket import create_connection
import websockets
#from client.tests.test_client_websocket import test_connection


def test_connection():
    async def inner():
        async with websockets.connect("ws://127.0.0.1:8000/ws/client/") as websocket:
            # await websocket.send("Hello, World!")
            print(f"> {await websocket.recv()}")
    return asyncio.get_event_loop().run_until_complete(inner())


if __name__ == "__main__":
    # print(test_connection())
    #w =  create_connection("ws://127.0.0.1:8000/ws/client/")
    '''
    w.send(json.dumps(
        {
            "action": "list",
            "request_id": "1"
        }
    ))
    '''
    #r = w.recv()
    # print(r)

    async def inner():
        async with websockets.connect("ws://127.0.0.1:8000/ws/client/") as websocket:
            # await websocket.send("Hello, World!")
            print(f"> {await websocket.recv()}")

    inner()
