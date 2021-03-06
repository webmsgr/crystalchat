import asyncio
import hashlib
import json
import multiprocessing as mp
import queue

import websockets

from crystalcommon import MessageTypes

clients = []
messages = []


class Client:
    def __init__(self, nickname, serverman):
        self.nickname = nickname
        self.server = server
        self.cid = None
        self.connected = False

    def ready(self):
        if self.connected:
            raise RuntimeError("Client already registered")
        self.cid = self.server.add_client(self)
        self.connected = True

    def leave(self):
        if not self.connected:
            raise RuntimeError("Client is not registered")
        self.server.remove_client(self.cid)
        self.cid = None
        self.connected = False

    def on_message(self, msg):
        if self.connected:
            self.server.on_message(self.cid, msg)
        else:
            raise RuntimeError("Client is not registered")

    def get_messages(self):
        if self.connected:
            return self.server.get_messages(self.cid)
        else:
            raise RuntimeError("Client is not registered")


class TheServer:
    """Manages clients, routes messages, etc."""

    def __init__(self):
        self.clients = []
        self.clientqueues = []
        self.messagequeue = mp.Queue()
        self.clientlock = mp.Lock()

    def add_client(self, client):  # Called on client join
        self.clientlock.acquire()
        if None in self.clients:
            clid = self.clients.index(None)
            self.clients[clid] = client
            self.clientqueues[clid] = mp.Queue()

        else:
            clid = len(self.clients)
            self.clients.append(client)
            self.clientqueues.append(mp.Queue())
        self.clientlock.release()
        return clid

    def remove_client(self, cid):  # called on client leave
        self.clientlock.acquire()
        self.clients[cid] = None
        self.clientlock.release()

    def get_messages(self, cid):  # Called by each websocket client
        queuetoget = self.clientqueues[cid]
        mess = []
        while True:
            try:
                mess.append(queuetoget.get(False))
            except queue.Empty:
                break
        return mess

    def send_message(self, cid, message, to):
        message = (cid, message)
        if to == "*":
            for num, client in enumerate(self.clients):
                if client:
                    self.clientqueues[num].put(message)
        for client in to:
            if self.clients[client]:
                self.clientqueues[client].put(message)

    def on_message(self, cid, raw_message):  # called by websocket clients
        self.messagequeue.put((cid, raw_message))

    def process_msg(self):
        msg = self.messagequeue.get()
        cid = msg[0]
        msg = self._process(cid, msg[1])
        self.send_message(cid, msg, "*")

    def _process(self, cid, msg):  # Override in subclass
        return msg


def server(sobj, hostname, port):
    eventloop = asyncio.new_event_loop()
    asyncio.set_event_loop(eventloop)

    async def websocketserver(websocket, path):
        async for message in websocket:
            # Simple echo server until i implement the real thing
            await websocket.send(message)

    # start a websocket server
    start_server = websockets.serve(websocketserver, hostname, port)
    eventloop.run_until_complete(start_server)
    eventloop.run_forever()


def startserver(hostname, port, sclass=TheServer):
    serverobj = sclass()
    sproc = mp.Process(target=server,
                       args=(serverobj, hostname, port),
                       daemon=True)
    sproc.start()
    while sproc.is_alive():
        serverobj.process_msg()
        


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
        try:
            await client.send(myid + b" has joined")
        except:
            clients.pop(clients.index(client))
    async for message in websocket:
        message = myid + b": " + message
        print(message)
        messages.append(message)
        for client in clients:
            try:
                await client.send(message)
            except:
                clients.pop(clients.index(client))
    clients.pop(clients.index(websocket))
    messages.append(myid + b" has left")
    for client in clients:
        await client.send(myid + b" has left")


if __name__ == "__main__":
    mp.freeze_support()
    start_server = websockets.serve(hello, "localhost", 42069)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
