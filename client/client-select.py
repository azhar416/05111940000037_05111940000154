import socket
import sys
import os
import math

sys.path.append('../')
import header_utils

HEADER_SIZE = 256
BUFFER_SIZE = 1024 
FORMAT = 'utf-8'

server_address = ('127.0.0.1', 5000)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(server_address)

def send_msg(message):
    msg = message.encode(FORMAT)
    header = header_utils.build_msg_header(msg)
    client_socket.send(header)
    client_socket.send(msg)

def recv_header():
    content_header = client_socket.recv(HEADER_SIZE).decode(FORMAT)
    return content_header

def recv_msg(header):
    msg_length = header_utils.read_msg_header(header)
    if msg_length:
        msg = client_socket.recv(int(msg_length)).decode(FORMAT)
        print(msg)
        return
    return

def recv_file(header):
    file_name, file_size = header_utils.read_file_header(header)
    max_loop = math.ceil(file_size / BUFFER_SIZE)
    counter = 0
    with open(f'{file_name}', 'wb') as f:
        while True:
            print('receiving data ...')
            data = client_socket.recv(BUFFER_SIZE)
            counter = counter + 1
            f.write(data)
            if counter == max_loop:
                break
    f.close()
    print('download success')

try:
    while True:
        # msg from server
        header = recv_header()
        header_type = header_utils.read_header_type(header)
        if header_type == 'msg':
            recv_msg(header)
        elif header_type == 'file':
            recv_file(header)

        print(">>", end=' ', flush=True)
        message = sys.stdin.readline()
        send_msg(message)

except KeyboardInterrupt:
    client_socket.close()
    sys.exit(0)
