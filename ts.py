import socket 
import os
import threading


def c2_send_command(commands, ip='127.0.0.1', port=5555):
    """Sends commands over TCP to the target."""
    print("Starting command server")
    socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print("c2_command",ip)
        socket_server.bind((ip, port))
        socket_server.listen(1)
    except Exception as e:
        print(f"exception in tcp {e}")
    while True:
        print("Listening for connections...")
        client_socket, addr = socket_server.accept()
        print("Connected by", addr)
        try:
            length = len(commands)
            client_socket.send(length.to_bytes(4, 'big'))
            for command in commands:
                client_socket.send(command.encode())
        finally:
            client_socket.close()

def c2_read_send(file, ip, port):
    """Reads commands from a file and sends each command."""
    print(" c2 read send")
    if os.path.exists(file):
        with open(file, 'r') as c_file:
            commands = [line.strip() for line in c_file]
            commands_str = '\n'.join(commands)
            c2 = threading.Thread(target=c2_send_command, args=(commands_str, ip, port))
            c2.start()
            c2.join()

