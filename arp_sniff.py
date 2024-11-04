from scapy.all import sniff, ARP
import time
import logging
from logging.handlers import RotatingFileHandler

class arp_parser:
    def __init__(self):
        
        self.arp_table = {}
        self.first_log_time = {}  
        self.counter = {}  # To count the number of spoofing detections
        self.max_counter = 20  # Maximum detections before logging

    def check_arp(self, packet):
        """Checks for ARP spoofing attempts and logs them with a counter mechanism."""
        if packet.haslayer(ARP):
            ip_src = packet[ARP].psrc
            mac_src = packet[ARP].hwsrc
            ip_dst = packet[ARP].pdst
            mac_dst = packet[ARP].hwdst

           
            if mac_src == "00:00:00:00:00:00" or mac_dst == "00:00:00:00:00:00":
                return  
            if ip_src in self.arp_table:
                if self.arp_table[ip_src] != mac_src:
                    if ip_src not in self.counter:
                        self.counter[ip_src] = 0
                        self.first_log_time[ip_src] = time.localtime()
                    self.counter[ip_src] += 1
                    
                    # Log if the counter reaches the max value
                    if self.counter[ip_src] >= self.max_counter:
                        self.log_spoof(ip_src, mac_src)
                        self.counter[ip_src] = 0  # Reset the counter after logging
            else:
                self.arp_table[ip_src] = mac_src

            # Check for spoofing attempts for destination IP
            if ip_dst in self.arp_table:
                if self.arp_table[ip_dst] != mac_dst:
                    # Increment counter for spoofing detection
                    if ip_dst not in self.counter:
                        self.counter[ip_dst] = 0
                    self.counter[ip_dst] += 1
                    
                    # Log if the counter reaches the max value
                    if self.counter[ip_dst] >= self.max_counter:
                        self.log_spoof(ip_dst, mac_dst)
                        self.counter[ip_dst] = 0  # Reset the counter after logging
            else:
                self.arp_table[ip_dst] = mac_dst

    def log_spoof(self, ip, mac):
        """Logs the spoofing event to the file."""
        local_time = time.localtime()
        formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
        formated_time2= time.strftime("%Y-%m-%d %H:%M:%S",self.first_log_time[ip])
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        logger = logging.getLogger('my_logger')
        handler = RotatingFileHandler('spoofedip.log', maxBytes=5*1024*1024, backupCount=3)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.warning(f"between {formated_time2}-{formatted_time}  - {ip} is spoofing {mac} - {self.max_counter} times ")
def start_sniffing(interface):
    """Sniff packets on the specified interface."""
    arp_detector = arp_parser()
    sniff(iface=interface, prn=arp_detector.check_arp)
