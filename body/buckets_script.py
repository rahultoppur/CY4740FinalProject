from tranco import Tranco
from datetime import date
from iso3166 import countries
import subprocess, threading, sys

obj = Tranco(cache=False, cache_dir='.tranco')
num_entries_per_piece = 20
num_entries = int(sys.argv[1])
lock = threading.Lock()
#latest_date = date.today().strftime("%Y-%m-%d")
latest_date = '2021-04-07'
latest_list = obj.list(date=latest_date).top(num_entries)
latest_list_pieces = []
#split list into chunks
for i in range (0, len(latest_list), num_entries_per_piece):
    latest_list_pieces.append(latest_list[i:i+num_entries_per_piece])
# testing with 20 lists of 5 entries each
dns_server = '@8.8.8.8' # using google's public DNS, inconsistent results using NS's from /etc/resolv.f
storage = {
            "fully_validated": [],
            "partially_validated": [],
            "not_supported": []
        }
countries_or_tlds = {}
weird = []

#latest_list.append('fail03.dnssec.works')
def put_into_buckets(latest_list_piece: list):
    
    for current_domain in latest_list_piece:
        results_for_domain = subprocess.run(["delv", dns_server, "+vtrace", "+multiline", current_domain], capture_output=True)
        #print(results_for_domain.stderr.decode())
        err = results_for_domain.stderr.decode()
        out = results_for_domain.stdout.decode()
        if 'fully validated' in out:
            storage['fully_validated'].append(current_domain)
        elif 'unsigned answer' in out:
            storage['partially_validated'].append(current_domain)
        elif 'SERVFAIL' in out or 'SERVFAIL' in err or 'resolution failed' in out or 'resolution failed' in err:
            storage['not_supported'].append(current_domain)
        else:
            weird.append({  "domain": current_domain,
                            "out": out,
                            "debug_info": err})
        domain_split = current_domain.split('.')
        last_index = len(domain_split) - 1
        tld = domain_split[last_index]
        try:
            tld = countries.get(tld).name
        except KeyError:
            dummy = False
        if tld in countries_or_tlds:
            countries_or_tlds[tld] += 1
        else:
            countries_or_tlds[tld] = 1

# needs to adjust for accuracy, first filter out generic TLDS then try country codes

threads = []
for i in range(len(latest_list_pieces)):
    t = threading.Thread(target=put_into_buckets, args=[latest_list_pieces[i]])
    threads.append(t)

for t in threads:
    t.start()

for t in threads:
    t.join()

print(storage)
print(weird)
print(countries_or_tlds)
