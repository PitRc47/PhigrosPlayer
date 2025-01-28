import socket

def start_server(host='192.168.1.28', port=7878):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print("Wait for Connection")

    client_socket, addr = server_socket.accept()
    print(f"Connection Received: {addr}")
    msg = client_socket.recv(81920)
    if msg:
        print("Message Received:")
        print(msg.decode('utf-8'))

if __name__ == "__main__":
    start_server()