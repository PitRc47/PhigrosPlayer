def start_client(server_ip='192.168.1.28', server_port=7878):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((server_ip, server_port))
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
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

import socket
client_socket = start_client()
try:
    import webview
    import webcv
    main()
except Exception as e:
    client_socket.sendall(e.encode('utf-8'))