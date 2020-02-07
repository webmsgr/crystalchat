#!/usr/bin/env python3
import click
import configparser
from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import Float, HSplit, VSplit, Window, WindowAlign
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.shortcuts import yes_no_dialog, button_dialog, input_dialog, message_dialog
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.eventloop import use_asyncio_event_loop
import rsa
import os
import websockets
import threading
import asyncio
from multiprocessing import Pipe
import queue
from prompt_toolkit.widgets import (
    Box,
    Button,
    Checkbox,
    Dialog,
    Frame,
    Label,
    ProgressBar,
    RadioList,
    TextArea,
)
import sys
def get_titlebar_text():
    return [
        ("class:title", " CrystalChat "),
        ("class:title", " (Press [Control-Q] to quit) "),
    ]

def startloop(loop: asyncio.BaseEventLoop):
    asyncio.set_event_loop(loop)
    loop.run_forever()
# @TODO make server and client not a echo server
# @BODY server is just a router. fix that plz
async def process_code(server,pipe,qevent):
    with patch_stdout():
        do = True
        async with websockets.connect(server) as websocket:
            while not qevent.is_set():
                if pipe.poll():
                    data = pipe.recv()
                    if data.upper() == "!DISCONNECT":
                        qevent.set()
                        break
                    if data.strip() == "":
                        continue
                    await websocket.send(data.encode("ascii"))
                try:
                    while True:
                        data = await asyncio.wait_for(websocket.recv(), timeout=0.5)
                        pipe.send(data.decode("ascii"))
                except asyncio.TimeoutError:
                    pass
# @TODO make the code good
# @BODY as it is, the code is really bad, really bad.
# @TODO public/private keys
# @BODY basic auth would be nice, and sign messages to the server.
@click.command()
def runclient():
    parser = configparser.ConfigParser()
    nloop = asyncio.new_event_loop()
    if os.path.exists("./server.conf") and yes_no_dialog("Server","Connect to last server?"):
        parser.read("server.conf")
        server = parser["server"]["server"]
        port = str(int(parser["server"]["port"]))
    else:
        server = input_dialog("Server","Enter Server IP/Hostname:")
        port = input_dialog("Server","Enter Port:")
        try:
            int(port)
        except:
            message_dialog("Server","Invalid Port")
            sys.exit(1)
        parser["server"]["server"] = server
        parser["server"]["port"] = port
        # save the server conf to file
    with open("server.conf","w") as cfile:
        parser.write(cfile)
    # connect to server
    messages = TextArea("",read_only=True)
    mes = []
    q = queue.Queue()
    def handle_message(buf):
        q.put(buf.text)
    inputbox = TextArea(height=1,multiline=False,accept_handler=handle_message)
    msgbody = Frame(messages)
    body = HSplit([
        msgbody,

        Window(height=1,char="#",style="class:line"),

        inputbox

    ])
    root = HSplit([
        Window(
            height=1,
            content=FormattedTextControl(get_titlebar_text),
            align=WindowAlign.CENTER
        ),
        Window(height=1, char=" ", style="class:line"),
        body
    ])
    kb = KeyBindings()
    @kb.add("c-c", eager=True)
    @kb.add("c-q", eager=True)
    def exitevent(event):
        q.put("!DISCONNECT")
        eventquit.set()
        event.app.exit()
        nloop.stop()
        t.join()
    app = Application(
        layout=Layout(root,focused_element=inputbox),
    key_bindings=kb,
    mouse_support=True,
    full_screen=True
    )
    async def update(serverpipe,qu):
        while True:
            while serverpipe.poll():
                data = serverpipe.recv()
                mes.append(data)
                out = "\n".join(mes)
                msgbody.body = TextArea(out)
                get_app().invalidate()
            try:
                while True:
                    dt = qu.get_nowait()
                    serverpipe.send(dt)
            except queue.Empty:
                pass
            await asyncio.sleep(0.5)
    t = threading.Thread(target=startloop,args=(nloop,),daemon=True)
    t.start()
    serversoc, cl = Pipe()
    eventquit = threading.Event()
    asyncio.run_coroutine_threadsafe(process_code("ws://{}:{}".format(server,port),cl,eventquit),nloop)
    asyncio.get_event_loop().create_task(update(serversoc,q))
    use_asyncio_event_loop(asyncio.get_event_loop())
    asyncio.get_event_loop().run_until_complete(app.run_async().to_asyncio_future())
if __name__ == "__main__":
    with patch_stdout():
        runclient()
