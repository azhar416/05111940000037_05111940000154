import math
import socket
import sys

sys.path.append('../')
import header_utils


HEADER = 256
BUFFER_SIZE = 1024
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "192.168.0.1"
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def get_header():
    header = client.recv(HEADER).decode(FORMAT)
    return header

def recv(header):
    msg_length = header_utils.read_msg_header(header)
    if msg_length:
        msg_length = int(msg_length)
        msg = client.recv(msg_length).decode(FORMAT)
        print(msg)

        return 1
    
    return 0

def send(msg):
    message = msg.encode(FORMAT)
    
    header = header_utils.build_msg_header(message)
    client.send(header)
    client.send(message)

def recv_file(header):
    file_name, file_size = header_utils.read_file_header(header)
    max_loop = math.ceil(file_size / BUFFER_SIZE)
    loop_counter = 0
    with open(f'{file_name}', 'wb') as f:
        while True:
            print('receiving data ...')
            data = client.recv(BUFFER_SIZE)
            loop_counter += 1
            f.write(data)
            if loop_counter == max_loop:
                break
            
    f.close()
    print('download success')

def start():
    connected = True
    while connected:

        # Get message from server
        header = get_header()
        msg_type = header_utils.read_header_type(header)
        if msg_type == 'file':
            recv_file(header)
        elif msg_type == 'msg':
            recv(header)

        print(">>", end=' ', flush=True)
        msg = input()
        send(msg)





start()