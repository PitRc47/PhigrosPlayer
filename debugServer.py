import socket
import os
import sys

sys.path.append('src')

#import main

def start_server(host='192.168.1.28', port=7878):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print("Wait for Connection")

    client_socket, addr = server_socket.accept()
    print(f"Connection Received: {addr}")
    with open('1.txt','w',encoding='utf-8') as f:
        try:
            while True:
                msg = client_socket.recv(81920)
                if msg:
                    print(msg.decode('utf-8'))
        except:
            pass

if __name__ == "__main__":
    start_server()