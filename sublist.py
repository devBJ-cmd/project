import sublist3r
import requests
import whois
from datetime import datetime
def domain_sub(domain):
 
    subdomains=sublist3r.main(domain,3,savefile=None,engines=None,ports=None,silent=True,verbose=False,enable_bruteforce=0)
    with open(f'{domain}.txt','a') as file:
        try:
            for subdomain in subdomains:
                w =whois.whois(domain)
                response=  requests.get(f'https://{subdomain}',timeout=5)
                status= response.status_code
                if isinstance(w.update, datetime):
                    update = w.update.strftime("%Y-%m-%d %H:%M:%S")
                elif isinstance(w.update, list) and w.update and isinstance(w.update[0], datetime):
                    update = w.update[0].strftime("%Y-%m-%d %H:%M:%S")  # Take the first date if it's a list
                else:
                    update = "Update date not available"
                file.write(f'{subdomain} {status} updated{update} \n ')
        except requests.ConnectionError:
            print(f'subdomain is down{subdomain}')
        except requests.Timeout:
            print(f"timeout :{subdomain} ")
    