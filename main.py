import sys
import os
import socket
import traceback
import logging

from io import StringIO

def start_client(server_ip='192.168.1.28', server_port=7878):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect_ex((server_ip, server_port))
    return client_socket
def webcv_start():
    import webcv
    
    root = webcv.WebCanvas(
        width = 1, height = 1,
        x = 0, y = 0,
        title = "PhigrosPlayer - Simulator",
        debug = False,
        resizable = False,
        frameless = False,
        renderdemand = False,
        renderasync = False,
        jslog = True,
        jslog_path = "./ppr-jslog-nofmt.js"
    )

client_socket = start_client()

stdout_buffer = StringIO()
stderr_buffer = StringIO()

sys.stdout = stdout_buffer
sys.stderr = stderr_buffer

log_buffer = StringIO()

class BufferingHandler(logging.StreamHandler):
    def __init__(self, buffer):
        super().__init__(buffer)

handler = BufferingHandler(log_buffer)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
root_logger = logging.getLogger()
root_logger.handlers = []
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(handler)

current_directory = os.getcwd()
logging.info(f'Current Path: {current_directory}')
for item in os.listdir(current_directory):
    full_path = os.path.join(current_directory, item)
    
    if os.path.isdir(full_path):
        print(f"Folder: {item}")
    else:
        print(f"File: {item}")

def main():
    webcv_start()

try:
    import webview
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(current_dir, 'src')
    sys.path.append(src_dir)

    main()
except Exception as e:
    error_message = f"Error occurred: {traceback.format_exc()}"
    captured_stdout = stdout_buffer.getvalue()
    captured_stderr = stderr_buffer.getvalue()
    captured_logs = log_buffer.getvalue()
    try:
        import time 
        message = f"{error_message}\nCaptured stdout:\n{captured_stdout}\nCaptured stderr:\n{captured_stderr}\nCaptured logs:\n{captured_logs}"
        client_socket.send(message.encode('utf-8'))
        time.sleep(1)
    except:
        pass