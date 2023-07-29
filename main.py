import threading
import socket
import os 
import pathlib
from OpenSSL import crypto, SSL
import ssl

HEADER = 64
IP = "0.0.0.0"
PORT = 5050
content_dir = "ctx/"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((IP, PORT))

if os.path.exists("cert.crt") and os.path.exists("private.key"):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain("cert.crt", "private.key")
else:
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 4096)
    cert = crypto.X509()
    cert.get_subject().CN = input("Type in hostname of this server: ")
    cert.set_serial_number(cert.get_serial_number())
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10*365*24*60*60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha512')
    with open("cert.crt", "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    with open("private.key", "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain("cert.crt", "private.key")
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
    while True:
        size = client.recv(HEADER).decode()
        if size:
            req = client.recv(int(size)).decode()
            if os.path.exists(content_dir + req):
                with open(content_dir + req, "rb") as f:
                    ctx = f.read()
                client.send(str(len(ctx)).encode() + b' ' * (HEADER - len(str(len(ctx)).encode())))
                client.send(ctx)
            else:
                client.send(str(len(b"404")).encode() + b' ' * (HEADER - len(str(len(b"404")).encode())))
                client.send(b"404")

def run():
    generate_index()
    server.listen()
    sock = context.wrap_socket(server, server_side = True)
    while True:
        client, address = sock.accept()
        threading.Thread(target=handle_req, args=(client, )).start()

run()
