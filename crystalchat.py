#!/usr/bin/env python3
import asyncio
import configparser
import os
import queue
import sys
import threading
from multiprocessing import Pipe
import requests
import click
import rsa
import websockets
import json
from crystalcommon import MessageTypes
from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import Float
from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.layout.containers import VSplit
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.containers import WindowAlign
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import button_dialog
from prompt_toolkit.shortcuts import input_dialog
from prompt_toolkit.shortcuts import message_dialog
from prompt_toolkit.shortcuts import yes_no_dialog
from prompt_toolkit.widgets import Box
from prompt_toolkit.widgets import Button
from prompt_toolkit.widgets import Checkbox
from prompt_toolkit.widgets import Dialog
from prompt_toolkit.widgets import Frame
from prompt_toolkit.widgets import Label
from prompt_toolkit.widgets import ProgressBar
from prompt_toolkit.widgets import RadioList
from prompt_toolkit.widgets import TextArea
import pkgutil
from prompt_toolkit.eventloop import use_asyncio_event_loop
#ENDREQ

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

tmp = configparser.ConfigParser()
tmp.read(resource_path("autoupdate/versions"))
try:
    ver = int(tmp["version"]["latest"])
except IndexError:
    print("Unable to read version config file.")
    sys.exit(1)
def get_titlebar_text():
    return [
        ("class:title", " CrystalChat v{}".format(ver)),
        ("class:title", " (Press [Control-Q] to quit) "),
    ]


def getkeys():
    if not os.path.exists("./keys"):
        os.mkdir("keys")
    haspub = "pubkey.key" in os.listdir("./keys")
    haspriv = "privkey.key" in os.listdir("./keys")
    if haspub and haspriv:
        # read the keys
    elif haspriv:
        # regen public key from private
    else:
        # generate and save new keys
    return None 


def startloop(loop: asyncio.BaseEventLoop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


# @TODO make server and client not a echo server
# @BODY server is just a router. fix that plz


async def process_code(server, pipe, qevent,isdis):
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
                        data = await asyncio.wait_for(websocket.recv(),
                                                      timeout=0.5)
                        pipe.send(data.decode("ascii"))
                except asyncio.TimeoutError:
                    pass
        isdis.set()


# @TODO make the code good
# @BODY as it is, the code is really bad, really bad.
# @TODO public/private keys
# @BODY basic auth would be nice, and sign messages to the server.
@click.command()
def runclient():
    parser = configparser.ConfigParser()
    nloop = asyncio.new_event_loop()
    if os.path.exists("./server.conf") and yes_no_dialog(
            "Server", "Connect to last server?"):
        parser.read("server.conf")
        server = parser["server"]["server"]
        port = str(int(parser["server"]["port"]))
    else:
        server = input_dialog("Server", "Enter Server IP/Hostname:")
        port = input_dialog("Server", "Enter Port:")
        try:
            int(port)
        except:
            message_dialog("Server", "Invalid Port")
            sys.exit(1)
        parser["server"] = {}
        parser["server"]["server"] = server
        parser["server"]["port"] = port
        # save the server conf to file
    with open("server.conf", "w") as cfile:
        parser.write(cfile)
    # connect to server
    nick = input_dialog("Nickname", "Enter a nickname:")
    if nick is None:
        nick = ""
    banned = "/."
    if any([x in banned for x in nick]):
        message_dialog("Nickname", "Invalid nickname")
    messages = TextArea("", read_only=True)
    mes = []
    q = queue.Queue()

    def handle_message(buf):
        q.put(buf.text)

    inputbox = TextArea(height=1,
                        multiline=False,
                        accept_handler=handle_message)
    msgbody = Frame(messages)
    body = HSplit(
        [msgbody,
         Window(height=1, char="#", style="class:line"), inputbox])
    root = HSplit([
        Window(
            height=1,
            content=FormattedTextControl(get_titlebar_text),
            align=WindowAlign.CENTER,
        ),
        Window(height=1, char=" ", style="class:line"),
        body,
    ])
    kb = KeyBindings()

    @kb.add("c-c", eager=True)
    @kb.add("c-q", eager=True)
    def exitevent(event):
        q.put("!DISCONNECT")
        eventquit.set()
        iscomplete.wait(1)
        event.app.exit()
        nloop.stop()
        myloop.stop()
        

    app = Application(
        layout=Layout(root, focused_element=inputbox),
        key_bindings=kb,
        mouse_support=True,
        full_screen=True,
    )

    async def update(serverpipe, qu):
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

    t = threading.Thread(target=startloop, args=(nloop, ), daemon=True)
    t.start()
    serversoc, cl = Pipe()
    iscomplete = threading.Event()
    eventquit = threading.Event()
    myloop = asyncio.new_event_loop()
    asyncio.set_event_loop(myloop)
    use_asyncio_event_loop(myloop)
    asyncio.run_coroutine_threadsafe(
        process_code("ws://{}:{}/{}".format(server, port,nick), cl, eventquit,iscomplete), nloop)
    asyncio.get_event_loop().create_task(update(serversoc, q))
    asyncio.get_event_loop().run_until_complete(
        app.run_async())
    myloop.run_forever()


def run():
    with patch_stdout():
        runclient()
if __name__ == "__main__":
    run()
