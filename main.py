import threading
import socket
import os 
import rsa
import pathlib

HEADER = 70000
IP = "0.0.0.0"
PORT = 5050
content_dir = "ctx/"

if os.path.exists("private_key.pem") and os.path.exists("public_key.pem"):
    pub_key = rsa.PublicKey.load_pkcs1(open("public_key.pem", "rb").read())
    priv_key = rsa.PrivateKey.load_pkcs1(open("private_key.pem", "rb").read())
else:
    pub_key, priv_key = rsa.newkeys(2048)
    with open("public_key.pem", "wb") as f:
        f.write(pub_key.save_pkcs1("PEM"))
    with open("private_key.pem", "wb") as f:
        f.write(priv_key.save_pkcs1("PEM"))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((IP, PORT))

def generate_index():
    index = []
    for i in list(pathlib.Path(content_dir).rglob("*")):
        if i.is_file():
            if "/".join(str(i).split("/")[1:]) == "index":
                continue
            else:
                index.append("/".join(str(i).split("/")[1:]))
    with open(content_dir + "index", "w") as f:
        f.write("\n".join(index))


def handle_req(client):
    client.send(str(len(pub_key.save_pkcs1("PEM"))).encode() + b' ' * (HEADER - len(str(len(pub_key.save_pkcs1("PEM"))).encode())))
    client.send(pub_key.save_pkcs1("PEM"))
    size = client.recv(HEADER).decode()
    if size:
        pub_con = rsa.PublicKey.load_pkcs1(client.recv(int(size)))
    while True:
        size = rsa.decrypt(client.recv(HEADER), priv_key).decode()
        if size:
            req = rsa.decrypt(client.recv(int(size)), priv_key).decode()
            if os.path.exists(content_dir + req):
                with open(content_dir + req, "rb") as f:
                    ctx = f.read()
                client.send(rsa.encrypt(str(len(ctx)).encode() + b' ' * (HEADER - len(str(len(ctx)).encode())), pub_con))
                client.send(rsa.encrypt(ctx), pub_con)
            else:
                client.send(rsa.encrypt(str(len(b"404")).encode() + b' ' * (HEADER - len(str(len(b"404")).encode())), pub_con))
                client.send(rsa.encrypt(b"404"), pub_con)

def run():
    generate_index()
    server.listen()
    while True:
        client, address = server.accept()
        threading.Thread(target=handle_req, args=(client, )).start()

run()
