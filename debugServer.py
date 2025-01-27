import socket

def start_server(host='192.168.1.28', port=7878):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print("Wait for Connection")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection Received: {addr}")
        try:
            msg = client_socket.recv(1024)
            if msg:
                print(f"从客户端接收到消息: {msg.decode('utf-8')}")
        except Exception as e:
            print(f"处理客户端消息时出错: {e}")
        finally:
            client_socket.close()

if __name__ == "__main__":
    start_server()