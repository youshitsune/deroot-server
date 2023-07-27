import threading
import socket
import os 

HEADER = 64
IP = "0.0.0.0"
PORT = 5050
content_dir = "ctx/"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((IP, PORT))

def handle_req(client):
    while True:
        size = client.recv(HEADER).decode()
        if size:
            req = client.recv(int(size)).decode()
            with open(content_dir + req, "rb") as f:
                ctx = f.read()
            client.send(str(len(ctx)).encode() + b' ' * (HEADER - len(str(len(ctx)).encode())))
            client.send(ctx)

def run():
    server.listen()
    while True:
        client, address = server.accept()
        threading.Thread(target=handle_req, args=(client, )).start()

run()

