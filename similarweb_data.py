#!/usr/bin/python3

import os
from tranco import Tranco
import pandas as pd
import subprocess
from subprocess import Popen, PIPE
import whois

# create a key of tlds and their types using detailed csv
tld_types = {} # tld: tld type
with open('whois/tld-list-details.csv','r') as f:
    for line in f:
        terms = line.strip().replace('"','').split(',')
        tld_types[terms[0]] = terms[1]

# make key of ccTLD to country code
country_codes = {} # country code: country name
country_names = {} # country name: country code
country_cctlds = {} # cctld: country code
with open('whois/IP2LOCATION-COUNTRY-INFORMATION/IP2LOCATION-COUNTRY-INFORMATION.CSV','r') as f:
    for line in f:
        terms = line.split(',')
        country_code = terms[0].replace('"','')
        country_name = terms[1].replace('"','')
        cctld = terms[-1].replace('"','').replace('\n','')
        country_codes[country_code] = country_name
        country_names[country_name.lower()] = country_code
        country_cctlds[cctld] = country_code

weird_results_map = {
    "redacted for privacy": None,
    "registrant phone: redacted": None,
    "registrant phone:": None,
    "redacted for gdpr": None,
    "malaysia": "MY",
    "china": "CN",
    "cyprus": "CY",
    "united states": "US",
    "nigeria": "NG",
    "ukraine": "UA",
    "fr": "FR",
    "ar": "AR",
    "gn": "GN",
    "india": "IN",
    "gdpr masked": None,
    "us": "US",
    "switzerland": "CH",
    "vietnam": "VN",
    "tw": "TW",
    "ha": "HT",
    "cn": "CN",
    "th": "TH",
    "sweden": "SE",
    "ci": "CI",
    "russian federation": "RU",
    "null": None,
    "data protected under gdpr": None,
    "redacted for privacy purposes": None,
    "tel. +": None,
    "statutory masking enabled": None,
    "viet nam": "VN",
    "中国": "CN",
    "personal data": None,
    "d:7 g.": None,
    "[owner_country]": None,
    "data redacted": None,
    "*******": None,
    "-": None,
    "0": None,
    "00": None,
    "usa": "US",
    "taiwan": "TW",
    "korea": "KR",
    "czech republic": "CZ",
    "united kingdom": "UK",
    "ukrain": "UA",
    "thaila": "TH",
    "united": None,
    "source:           uaepp": "UA",
    "bangko": "TH",
    "un": None,
    "sing": "SG",
    "indone": "ID",
    "istanb": "TR",
    "slovak republic": "SK",
    "macau": "MO",
    "viet n": "VN",
    "MALAYS": "MY",
    "an": "AD",
    "turkiy": "TR",
    "zh": None,
    "nether": "NL",
    "hong k": "HK",
    "muang": None,
    "hakkari": None,
    "yu": None,
    "kv": None,
    "cs": "CR",
    "moldova": "MD",
    "switze": "CH",
    "aust": "AU",
    "tx": "TM",
    "tp": "ST",
    "ho": "HN",
    "ita": "IT",
    "malays": "MY",
    "ac": "AG",
    "sw": "SW"
}

def resolve_country_result(result):
    if country_codes.get(country_result) != None: return country_result
    elif country_codes.get(country_result.upper()) != None: return country_result.upper()
    elif country_names.get(country_result.lower()) != None: return country_names.get(country_result.lower())
    elif weird_results_map.get(country_result.strip().lower(), 0) != 0: return weird_results_map.get(country_result.lower().strip())
    elif "registrant phone" in country_result.lower(): return None
    else: return None

data = {} # site: [rank, tld, tld_type, country, delv_result]
with open("MASTER_RESULTS.csv","r") as f:
    for line in f:
        terms = line.strip().split(',')
        data[terms[0]] = [terms[1],terms[2],terms[3],terms[4],terms[5]]

# basic tranco data
contents = os.listdir('similarweb')
for c in contents:
    if "_Data" not in c:
        file_data = {}

        with open(f"similarweb/{c}","r") as f:
            for line in f:
                terms = line.strip().replace('\t',' ').split(' ')
                print(terms)
                rank = terms[0]
                site = terms[1]
                file_data[site] = data.get(site)
                if data.get(site) != None:
                    file_data[site].append(rank)
                else:
                    tld = site.split('.')[-1]
                    tld_type = tld_types.get(tld)
                    if tld_type == "ccTLD":
                        country = country_cctlds[tld]
                    else:
                        try:
                            query = whois.query(site)
                        except:
                            query = None
                        try:
                            if query.registrant_country:
                                country = resolve_country_result(query.registrant_country)
                            else:
                                country = ''
                        except:
                            country = ''
                    results_for_domain = subprocess.Popen(["delv", "@8.8.8.8", "+vtrace", "+multiline", site], stdout=PIPE, stderr=PIPE)
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
                    delv_result = score
                    file_data[site] = [None, tld, tld_type, country, delv_result, rank]

        sites = []
        ranks = []
        tlds = []
        tld_types_list = []
        countries = []
        delv_results = []
        category_ranks = []
        for site in file_data:
            info = file_data.get(site)
            if info != None:
                sites.append(site)
                ranks.append(info[0])
                tlds.append(info[1])
                tld_types_list.append(info[2])
                countries.append(info[3])
                delv_results.append(info[4])
                category_ranks.append(info[5])
            else:
                sites.append(site)
                ranks.append(None)
                tlds.append(None)
                tld_types_list.append(None)
                countries.append(None)
                delv_results.append(None)
                category_ranks.append(info[0])

        df = pd.DataFrame(data={"site":sites, "category_rank":category_ranks, "tranco_rank":ranks, "tld":tlds, "tld_type":tld_types_list, "country":countries, "delv_result":delv_results})
        print(df)
        df.to_csv(f"similarweb/{c.split('.')[0]}_Data.csv",index=False)
