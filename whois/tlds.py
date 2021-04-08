#!/usr/bin/python3

# - (Maggie) create list of common TLDs

import os
from tranco import Tranco
import pandas as pd

# whois cbw.sh | grep "Registrant Country"
# Registrant Country: US
# whois cbw.sh | grep "Registrant State/Province"
# Registrant State/Province: CA

# get tranco list
t = Tranco(cache=True, cache_dir='.tranco')
tranco_list = t.list()

# get list of all relevant tlds from tranco list, create lists of sites with each tld
tld_lists = {}
relevant_tlds = []
for site in tranco_list.top(1000000):
    tld = site.split('.')[-1]
    try:
        tld_lists[tld].append(site)
    except:
        tld_lists[tld] = [site]
        relevant_tlds.append(tld)

# create a key of tlds and their types using detailed csv
tld_types = {}
with open('tld-list-details.csv','r') as f:
    for line in f:
        terms = line.strip().replace('"','').split(',')
        tld_types[terms[0]] = terms[1]

# create lists of tlds by type
country_tlds = []
generic_tlds = []
odd_tlds = []
error_tlds = []
for tld in relevant_tlds:
    try:
        if tld_types[tld] == "ccTLD": country_tlds.append(tld)
        elif tld_types[tld] in ["gTLD","sTLD","grTLD"]: generic_tlds.append(tld)
        else: odd_tlds.append((tld,tld_types[tld]))
    except:
        error_tlds.append(tld)

# save typed lists of tlds to files
with open('country-tlds','w') as f:
    for tld in country_tlds: f.write(f"{tld}\n")
with open('generic-tlds','w') as f:
    for tld in generic_tlds: f.write(f"{tld}\n")
with open('odd-tlds','w') as f:
    for tld in odd_tlds: f.write(f"{tld[0]},{tld[1]}\n")
with open('error-tlds','w') as f:
    for tld in error_tlds: f.write(f"{tld}\n")

# make lists of tranco sites for each tld and directory to store in
if not os.path.exists('tld_lists'):
    os.makedirs('tld_lists')
for tld in relevant_tlds:
    with open(f"tld_lists/{tld}","w") as f:
        for site in tld_lists[tld]: f.write(f"{site}\n")

sites = []
tlds = []
countries = []
ranks = []

# make key of ccTLD to country code
country_codes = {}
country_cctlds = {}
with open('IP2LOCATION-COUNTRY-INFORMATION/IP2LOCATION-COUNTRY-INFORMATION.CSV','r') as f:
    for line in f:
        terms = line.split(',')
        country_code = terms[0].replace('"','')
        country_name = terms[1].replace('"','')
        cctld = terms[-1].replace('"','').replace('\n','')
        country_codes[country_code] = country_name
        country_cctlds[cctld] = country_name

whois_countries = []
whois_tlds = generic_tlds
none_count = 0
success_count = 0
count = 0
# need to get sites for each relevant tlds
for tld in whois_tlds:
    with open(f'tld_lists/{tld}','r') as f:
        count = 0
        for line in f:
            if count < 5:

                site = line.strip()

                # gather and store whois data
                output = os.popen(f"whois {site} | grep \"Registrant Country\"").read()
                if "Registrant" not in output:
                    country = None
                    country_output = None
                    none_count += 1
                else:
                    country_output = output.split(':')[-1].strip()
                    if country_output not in whois_countries:
                        whois_countries.append(country_output)
                        print(country_output)
                    success_count += 1
                    # if len(country_output) > 2:
                    #     country = country_output
                    # else:
                    #     country = country_codes[country_output.upper()]
                sites.append(site)
                tlds.append(tld)
                ranks.append(tranco_list.rank(site))
                countries.append(country_output)
            count += 1

# print(f"sites that need whois: {count}")

with open('whois-countries','w') as f:
    for country in whois_countries: f.write(f"{country}\n")

print(f'success count: {success_count}')
print(f'none count: {none_count}')

count = 0
# add sites with ccTLD to lists for making dataframe
# for tld in country_tlds:
#     with open(f'tld_lists/{tld}','r') as f:
#         for line in f:
#             if count < 2000:
#                 site = line.strip()
#
#                 # gather and store whois data
#                 country = country_cctlds[tld]
#                 sites.append(site)
#                 tlds.append(tld)
#                 ranks.append(tranco_list.rank(site))
#                 countries.append(country)
#             count += 1

# print(f"sites that don't need whois: {count}")

# make dataframe and save to csv
df = pd.DataFrame(data={"site":sites, "tld":tlds, "rank":ranks, "country":countries})
print(df)
df.to_csv('tld-sampler.csv',index=False)
