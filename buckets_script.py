from tranco import Tranco
from datetime import date
from iso3166 import countries
import subprocess

obj = Tranco(cache=False, cache_dir='.tranco')
#latest_date = date.today().strftime("%Y-%m-%d")
latest_date = '2021-04-07'
latest_list = obj.list(date=latest_date).top(100)
dns_server = '@8.8.8.8' # using google's public DNS, inconsistent results using NS's from /etc/resolv.f
storage = {
            "fully_validated": [],
            "partially_validated": [],
            "not_supported": []
        }
countries_or_tlds = {}
weird = []

#latest_list.append('fail03.dnssec.works')

for current_domain in latest_list:
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

print(storage)
print(weird)
print(countries_or_tlds)
