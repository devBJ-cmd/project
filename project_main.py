import c2_client
import c2_server
import argparse
import sublist
import arp_sniff
import threading

def main():

    parser=argparse.ArgumentParser(description="toolbox for security c2 client c2 server arpspoof detector and sublister")
    parser.add_argument("-mode",choices=["c2_client","c2_server","arp_spoofdetect","sublister"],help= """choose between the diffrent tools c2 client 
                        c2 server arp spoof detector and sublister if you choose c2_client or c2_server the other one will start aswell it will start an http server that will run on port 8000 on windows it must be run as adminstrator """)
    parser.add_argument("-tfile",help="give filename that the server will read and transfer the files")
    parser.add_argument("-filelist", help= "filename to the client that it will read and know where to save the files ",type = str)
    parser.add_argument("-cmdfile",help="give filename that that contains commands that the server will run ",type = str)
    parser.add_argument("-server_ip",help="provide an ip that the server will run on,",type= str)
    parser.add_argument("-client_ip",help="provide an ip that the client will run on",type=str)
    parser.add_argument("-crypt_ip",help="provide an ip that the client will run on",type=str)
    parser.add_argument("-domain",help="provide a domain that will be used with sublister will save the data to domain.txt ")
    parser.add_argument("-interface",help="provide a interface that will be used for the arp spoof detector ",type=str)
    args=parser.parse_args()
    print("args.mode is",args.mode)
    if (args.mode == 'c2_client'): 
        try:
            c1=threading.Thread(target=c2_client.start,args=(args.cmdfile,args.filelist,args.client_ip)) #
            c1.start()
            c2=threading.Thread(target=c2_server.c2_server,args=(args.server_ip,args.tfile,args.crypt_ip))
            c2.start()       
        except Exception as e:
            print(f"eception in creating thread {e}")
    if  (args.mode == 'c2_server'):
        try:
            c1=threading.Thread(target=c2_client.start,args=(args.cmdfile,args.filelist,args.client_ip)) #
            c1.start()
            c2=threading.Thread(target=c2_server.c2_server,args=(args.server_ip,args.tfile,args.crypt_ip))
            c2.start()       
        except Exception as e:
            print(f"eception in creating thread {e}")   
    if args.mode == 'arp_spoofdetect':
        if args.interface:
            arp_sniff.start_sniffing(args.interface)
        else:
            print("Error: Please provide a valid network interface for ARP spoof detection.")
    if args.mode == 'sublister':
            sublist.domain_sub(args.domain)


if __name__ == '__main__':
    main()