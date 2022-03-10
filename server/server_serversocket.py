import os
from pickle import TRUE
import socket
import socketserver
import sys
import threading
from os import walk

sys.path.append('../')
import header_utils

# Constants
HEADER = 256
BUFFER_SIZE = 1024
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
DATASET = './dataset'

files = []

def listFiles():
    files = next(walk(DATASET), (None, None, []))[2]
    message = "List of files :\n"
    for idx, f in enumerate(files):
        message += f"{idx} : {f}\n"

    return message

def send(conn, addr, msg):
    
    message = msg.encode(FORMAT)
    
    header = header_utils.build_msg_header(message)
    print(f'[SENDING] Server is sending {len(msg)} bytes of data to {addr}')
    conn.send(header)
    conn.send(message)

def recv(conn, addr):
    header = conn.recv(HEADER).decode(FORMAT)
    msg_length = header_utils.read_msg_header(header)
    if msg_length:
        msg_length = int(msg_length)
        msg = conn.recv(msg_length).decode(FORMAT)
        print(f"[{addr}] {msg}")

        if(msg != DISCONNECT_MESSAGE):
            return msg
            
    return 0

def send_file(conn, addr, file):
    file_path = f'{DATASET}/{file}'
    if os.path.isfile(file_path):
        file_size = os.path.getsize(file_path)
        header = header_utils.build_file_header(file, file_size)
        print(f'[SENDING] Server is sending file {file} to {addr}')
        conn.send(header)
        f = open(file_path, 'rb')
        l = f.read(1024)
        while l:
            conn.send(l)
            l = f.read(BUFFER_SIZE)
        print(f'[SUCCESS] Server successfully send file {file} to {addr}')
        f.close()
    else:
        print(f'[ERROR] Server failed to send file {file} to {addr}')

    

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    send(conn, addr, f"{listFiles()}Select file you want to download with command 'unduh nama_file'")
    connected = True
    while connected:
        res = recv(conn, addr)
        if not res:
            connected = False
        else:
            cmd = res.split(' ')
            if cmd[0] == 'unduh':
                dl_file = cmd[1]
                send_file(conn, addr, dl_file)
            else:
                send(conn, addr, "Invalid command, please try again")

            
    conn.close()

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        print(f"[LISTENING] Server is listening on {SERVER}")
        while True:
            handle_client(self.request,self.client_address)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def start():
    # server.listen()
    server = ThreadedTCPServer(ADDR, MyTCPHandler)
    with server:
        server.serve_forever()
    
        # thread = threading.Thread(target=handle_client, args=(conn, addr))
        # thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")
        
print("[STARTING] server is starting ...")
start()