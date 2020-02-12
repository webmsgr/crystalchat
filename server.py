import asyncio
import hashlib
import json
from crystalcommon import MessageTypes
import websockets
import multiprocessing as mp
import queue
clients = []
messages = []


class TheServer:
    """Manages clients and crap, routes messages, etc."""
    def __init__(self):
        self.clients = []
        self.clientqueues = []
        self.messagequeue = mp.Queue()
        self.clientlock = mp.Lock()
    def add_client(self,client): # Called on client join
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
        return self.clid
    def removeclient(self,cid): # called on client leave
        self.clientlock.acquire()
        self.clients[cid] = None
        self.clientlock.release()
    def get_messages(self,cid): # Called by each websocket client
        queuetoget = self.clientqueues[cid]
        mess = []
        while True:
            try:
                mess.append(queuetoget.get(False))
            except queue.Empty:
                break
        return mess
    def send_message(self,cid,message,to):
        message = (cid,message)
        for client in to:
            if self.clients[client]:
                self.clientqueues[client].put(message)
    def on_message(self,cid,raw_message): # called by websocket clients
        self.messagequeue.put((cid,raw_message))
    def process_msg(self):
        msg = self.messagequeue.get()
        cid = msg[0]
        msg = self._process(msg[1])
        self.send_message(cid,msg,[])
    def _process(self,msg):
        return msg
    def start_server(self): # Starts a websocket server in another thread.
        raise NotImplemented
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


start_server = websockets.serve(hello, "localhost", 42069)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
