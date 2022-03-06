import socket
import select
import sys
import os

sys.path.append('../')
import header_utils

BUFFER_SIZE = 1024
HEADER_SIZE = 256
FORMAT = 'utf-8'

server_address = ('127.0.0.1', 5000)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(server_address)
server_socket.listen(5)

input_socket = [server_socket]

dataset = './dataset'
files = []
def dataset_list_file():
    files = next(os.walk(dataset), (None, None, []))[2]
    message = "List of files :\n"
    for idx, f in enumerate(files):
        message += f"{idx} : {f}\n"
    return message

def send_msg(sock, msg):
    message = msg.encode(FORMAT)
    header = header_utils.build_msg_header(message)
    print(f'[SENDING] Server is sending {len(msg)} bytes of data')
    sock.send(header)
    sock.send(message)

def recv_msg(sock):
    header = sock.recv(HEADER_SIZE).decode(FORMAT)
    msg_length = header_utils.read_msg_header(header)
    if msg_length:
        msg = sock.recv(int(msg_length)).decode(FORMAT)
        print(sock.getpeername(), msg)
        return msg
    return 0

def send_file(sock, file_name):
    file_path = f"{dataset}/{file_name}"
    if os.path.isfile(file_path):
        file_size = os.path.getsize(file_path)
        header = header_utils.build_file_header(file_name, file_size)
        print(f'[SENDING] Server is sending file {file_name}')
        sock.send(header)
        with open(file_path, 'rb') as f:
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    print(f'[SUCCESS] Server successfully send file { file_name }')
                    break
                sock.sendall(bytes_read)
        f.close()
    else:
        print(f'[ERROR] Server failed to send file { file_name }')

try:
    while True:
        read_ready, write_ready, exception = select.select(input_socket, [], [])

        for sock in read_ready:
            if sock == server_socket:
                client_socket, client_address = server_socket.accept()
                input_socket.append(client_socket)        
            else:
                received_message = recv_msg(sock)
                if received_message:
                    command = received_message.split(" ")
                    if command[0] == "unduh":
                        file_name = command[1].strip("\n")
                        send_file(sock, file_name)
                    elif command[0].strip('\n') == "list":
                        send_msg(sock, f"{dataset_list_file()}Select file you want to download with command 'unduh nama_file'")
                    else:
                        send_msg(sock, "Invalid command, please try again")
                else:
                    sock.close()
                    input_socket.remove(sock)

except KeyboardInterrupt:        
    server_socket.close()
    sys.exit(0)
