import init_logging as _

import webcv
import asyncio
import random
import threading
import websockets
import json
import logging

class ValueEvent:
    def __init__(self):
        self.e = threading.Event()
    
    def set(self, value):
        self.value = value
        self.e.set()

    def wait(self):
        self.e.wait()
        return self.value

def start_server(window: webcv.WebCanvas, addr: str, port: int):
    client = ValueEvent()
    tasks: dict[int, ValueEvent] = {}
    split_magic = "\x00"
    
    async def main_logic(ws: websockets.WebSocketServerProtocol, path: str):
        nonlocal client
        client.set(ws)
        
        while True:
            recv = await ws.recv()
            
            for rawdata in recv.split(split_magic):
                if not rawdata: continue
                data = json.loads(rawdata)
                
                match data["type"]:
                    case "evaljs_result":
                        tasks[data["tid"]].set(data.get("result", None))
                    
                    case "jsapi_callback":
                        window.jsapi.call_attr(data["name"], *data["args"])
            
    def evaljs(
        code: str,
        needresult: bool = True,
        *args, **kwargs
    ):
        tid = random.randint(0, 2 << 31)
        tasks[tid] = ValueEvent()
        asyncio.run(client.wait().send(json.dumps({
            "type": "evaljs",
            "code": code,
            "tid": tid
        }, ensure_ascii=False) + split_magic))
        
        if needresult:
            return tasks[tid].wait()
    
    while True:
        try:
            server = websockets.serve(main_logic, addr, port)
            asyncio.get_event_loop().run_until_complete(server)
            threading.Thread(target=asyncio.get_event_loop().run_forever, daemon=True).start()
        except Exception as e:
            logging.error(f"start server on port {port} failed: {repr(e)}")
            if port > 65535:
                raise Exception("port out of range")
            port += 1
            continue
        break
    
    return evaljs

def hook(window: webcv.WebCanvas):
    try: asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())
        
    window.evaljs = start_server(window, "", 8080)
