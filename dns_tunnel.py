import socket
from scapy.all import IP,DNS,UDP,DNSQR 
import os
import base64
def simple_decrypt(string, ip):
    """Decrypts a string that was encrypted with simple_encrypt."""
    blah = ip.split('.')
    i = 0 
    org_string = []
    # Decode the base64 string
    try:
        # Ensure string is in bytes
        if isinstance(string, bytes):

            b64decode = base64.b64decode(string)
        elif isinstance(string, str):
            b64decode = base64.b64decode(string.encode('utf-8'))
        else:
            raise ValueError("Input must be a string or bytes")

        # XOR decode each byte using the corresponding IP segment
        for byte in b64decode:
            decode_char = chr(byte ^ int(blah[i]))  # Directly use byte
            org_string.append(decode_char)
            i += 1
            if i == 4:  # Loop through the IP segments
                i = 0

        decoded = ''.join(org_string)
        return decoded
    except Exception as e:
        print(f"An error occurred: {e}")
        return None  # Return None or handle error appropriately
def write_to_file(file_content, file_list):
    """Write the content to the first filename found in file_list and remove that filename from the list."""
    write_this_file=""
    with open(file_list, 'r+') as file:
        filenames = file.readlines()
        filenames = [line.strip() for line in filenames if line.strip()]
       
        if filenames:
            write_this_file = filenames.pop(0)
            file.seek(0)
            file.writelines(f"{filename}\n" for filename in filenames)
            file.truncate() 

    
    with open(write_this_file, 'a') as target_file:
        target_file.write(file_content)

def recive_dns(ip,file_list):
    """ip is where from the files should be recived file_list is a file that contains each file that should be sent from other part"""
    client = socket.socket(socket.AF_INET,socket.SOCK_RAW,socket.IPPROTO_UDP)
    send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # For sending
    header={}
    final_string=""
    msg_recived=0
    sequence=0
    try:
        send_socket.bind((ip,8333))
        client.bind((ip,8222))
        send_socket.listen()
    except Exception as e:
        print(f' error connection {e}')
    while(True):
        sock,addr =send_socket.accept()
        data, addr = client.recvfrom(1024)
        if( not data ):
            break
        packet= IP(data)
        if UDP in packet:
            udp_payload = packet[UDP].payload  # problem with scapy could not unpack at once
            dns_packet = DNS(udp_payload.load)  
            if dns_packet[DNS].qd:
                qname = dns_packet[DNSQR].qname.decode() 
                sequence =int(qname[0])
                nr_of_msg=int(qname[1])
                msg_recived+=1
                length_to_msg= int(qname[2:4])+1
                ip=qname[4:length_to_msg]
                header[sequence]=simple_decrypt((str(qname[length_to_msg:len(qname)]).rstrip('.')),ip) #need to rstrip because scapy adds a dot
                sock.send(str(sequence).encode())
        if sequence in header and msg_recived ==nr_of_msg :
            for x in header.items():
                final_string += x[1]
            header={}
            nr_of_msg=0
            msg_recived=0
            sequence=0
            write_to_file(final_string,file_list)  
            final_string=""
    client.close()
    sock.close()
    return 0
    
     

