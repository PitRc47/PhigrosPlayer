import sys
import os
import socket
import traceback

def start_client(server_ip='192.168.1.28', server_port=7878):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect_ex((server_ip, server_port))
    return client_socket
def main():
    root = webcv.WebCanvas(
        width = 1, height = 1,
        x = 0, y = 0,
        title = "PhigrosPlayer - Simulator",
        debug = True,
        resizable = False,
        frameless = False,
        renderdemand = False,
        renderasync = False,
        jslog = True,
        jslog_path = "./ppr-jslog-nofmt.js"
    )
    while True:
        root.run_js_code("console.log('Hello, World!');")

client_socket = start_client()
try:
    import webview

    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(current_dir, 'src')
    sys.path.append(src_dir)

    import webcv
    main()
    
except Exception as e:
    error_message = f"Error occurred: {traceback.format_exc()}"
    print(error_message)
    try:
        client_socket.send(error_message.encode('utf-8'))
    except:
        pass