#from tranco import Tranco
#from datetime import date
#from iso3166 import countries
import subprocess, threading, sys, csv
from subprocess import Popen, PIPE
#obj = Tranco(cache=False, cache_dir='.tranco')
num_entries = 10#int(sys.argv[1])
num_entries_per_piece = 932#int(sys.argv[2])
lock = threading.Lock()
#latest_date = date.today().strftime("%Y-%m-%d")
#latest_date = '2021-04-07'
#latest_list = obj.list(date=latest_date).top(num_entries)
latest_list_pieces = []
#split list into chunks, write to input files
#FIXME: CHANGE THE FILE INPUT HERE
data = open('negatives_emily.csv', 'r')
latest_list = list(csv.reader(data))

count = 0
for i in range (0, len(latest_list), num_entries_per_piece):
    chunk = latest_list[i:i+num_entries_per_piece]
    infile = open(f"./input/{count:02}", "w")
    for entry in chunk:
        infile.write(str(entry) + "\n")
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
        domain = current_domain[1:-2].replace("\'", "").replace(" ", "").split(',')
        results_for_domain = subprocess.Popen(["delv", dns_server, "+vtrace", "+multiline", domain[1]], stdout=PIPE, stderr=PIPE)
        out, err = results_for_domain.communicate()
        err = err.decode()
        out = out.decode()
        score = "-2"
        if 'fully validated' in out:
            score = "1"
        elif 'unsigned answer' in out:
            score = "0"
        elif 'SERVFAIL' in out or 'resolution failed' in out:
            score = "-1"
        write_output(domain[0] + "," + domain[1] + "," + score + "\n", t_num)

# needs to adjust for accuracy, first filter out generic TLDS then try country codes

threads = []
for i in range(count):
    t = threading.Thread(target=put_into_buckets, args=[f"{i:02}"])
    threads.append(t)
    t.start()

for t in threads:
    t.join()
