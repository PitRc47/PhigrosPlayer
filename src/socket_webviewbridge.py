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
    server_loop = None  # 存储服务器的事件循环

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
        
        # 使用服务器的事件循环提交任务
        future = asyncio.run_coroutine_threadsafe(
            client.wait().send(
                json.dumps({
                    "type": "evaljs",
                    "code": code,
                    "tid": tid
                }, ensure_ascii=False) + split_magic
            ),
            server_loop  # 确保使用服务器线程的loop
        )
        future.result()  # 等待发送完成
        
        return tasks[tid].wait() if needresult else None

    while True:
        try:
            # 始终创建新的事件循环
            server_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(server_loop)
            
            # 启动WebSocket服务器
            start_server = websockets.serve(main_logic, addr, port)
            server = server_loop.run_until_complete(start_server)
            
            # 启动事件循环线程
            def run_loop():
                asyncio.set_event_loop(server_loop)
                server_loop.run_forever()
                
            threading.Thread(target=run_loop, daemon=True).start()
            
        except Exception as e:
            logging.error(f"start server({addr}) on port {port} failed: {repr(e)}")
            if port > 65535:
                raise Exception("port out of range")
            port += 1
            continue
        break
    
    return evaljs

def hook(window: webcv.WebCanvas):
    window.evaljs = start_server(window, "", 8080)
