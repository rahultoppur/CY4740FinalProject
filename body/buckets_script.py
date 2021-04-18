from tranco import Tranco
from datetime import date
from iso3166 import countries
import subprocess, threading, sys

obj = Tranco(cache=False, cache_dir='.tranco')
num_entries = int(sys.argv[1])
num_entries_per_piece = int(sys.argv[2])
lock = threading.Lock()
#latest_date = date.today().strftime("%Y-%m-%d")
latest_date = '2021-04-07'
latest_list = obj.list(date=latest_date).top(num_entries)
latest_list_pieces = []
#split list into chunks, write to input files
count = 0
for i in range (0, len(latest_list), num_entries_per_piece):
    chunk = latest_list[i:i+num_entries_per_piece]
    infile = open(f"./input/{count:02}", "w")
    for entry in chunk:
        infile.write(entry + "\n")
    infile.close()
    count += 1

dns_server = '@8.8.8.8' # using google's public DNS, inconsistent results using NS's from /etc/resolv.f
storage = {
            "fully_validated": [],
            "partially_validated": [],
            "not_supported": []
        }
countries_or_tlds = {}
weird = []

def write_output(output: str, t_num: int):
    outfile = open(f"./output/{t_num}", "a")
    outfile.write(output)
    outfile.close()

#latest_list.append('fail03.dnssec.works')
def put_into_buckets(t_num: int):
    infile = open(f"./input/{t_num}","r")
    list_of_domains = infile.readlines()
    infile.close()
    for current_domain in list_of_domains:
        results_for_domain = subprocess.run(["delv", dns_server, "+vtrace", "+multiline", current_domain.strip()], capture_output=True)
        err = results_for_domain.stderr.decode()
        out = results_for_domain.stdout.decode()
        score = "-2"
        if 'fully validated' in out:
            score = "1"
        elif 'unsigned answer' in out:
            score = "0"
        elif 'SERVFAIL' in out or 'SERVFAIL' in err or 'resolution failed' in out or 'resolution failed' in err:
            score = "-1"
        write_output(current_domain.strip() + "," + score + "\n", t_num)

# needs to adjust for accuracy, first filter out generic TLDS then try country codes

threads = []
for i in range(count):
    t = threading.Thread(target=put_into_buckets, args=[f"{i:02}"])
    threads.append(t)

for t in threads:
    t.start()

for t in threads:
    t.join()
