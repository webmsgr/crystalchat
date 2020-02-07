import asyncio
import hashlib

import websockets

clients = []
messages = []


async def hello(websocket, path):
    print(path)
    myid = hashlib.new("md5")
    myid.update(websocket.remote_address[0].encode("ascii"))
    myid = myid.hexdigest().encode("ascii")
    if path != "/":
        myid += ("({})".format(path.split("/")[1])).encode("ascii")
    clients.append(websocket)
    if len(messages) < 10:
        for message in messages:
            await websocket.send(message)
    else:
        for message in messages[-9:]:
            await websocket.send(message)
    messages.append(myid + b" has joined")
    for client in clients:
        await client.send(myid + b" has joined")
    async for message in websocket:
        message = myid + b": " + message
        print(message)
        messages.append(message)
        for client in clients:
            await client.send(message)
    clients.pop(clients.index(websocket))
    messages.append(myid + b" has left")
    for client in clients:
        await client.send(myid + b" has left")


start_server = websockets.serve(hello, "localhost", 42069)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
