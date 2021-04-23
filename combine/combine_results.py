#!/usr/bin/python3

import os
from tranco import Tranco
import pandas as pd

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

# basic tranco data
sites_info = {} # site: [rank, tld, tld_type]
cctld_sites = {} # site: country code
with open("TRANCO_1M_MASTER.csv","r") as f:
    for line in f:
        terms = line.strip().split(',')
        rank = terms[0]
        site = terms[1]
        tld = site.split('.')[-1]
        tld_type = tld_types.get(tld)
        if tld_type == "ccTLD":
            cctld_sites[site] = country_cctlds[tld]
        sites_info[site] = [rank, tld, tld_type]

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

# whois_results
whois_results = {} # site: country code
with open("whois_results.csv","r") as f:
    for line in f:
        terms = line.strip().split(',')
        site = terms[0]
        country_result = terms[1]
        if country_codes.get(country_result) != None:
            whois_results[site] = country_result
        else:
            whois_results[site] = resolve_country_result(country_result)

# rahul's domains
with open("rahul-domains-clean","r") as f:
    for line in f:
        terms = line.strip().split(',')
        site = terms[0]
        country_result = terms[1]
        if cctld_sites.get(site) != None:
            if country_codes.get(country_result) != None:
                whois_results[site] = country_result
                del cctld_sites[site]
            else:
                resolved = resolve_country_result(country_result)
                if resolved != None: whois_results[site] = resolved
        else:
            if country_codes.get(country_result) != None:
                whois_results[site] = country_result
            else:
                whois_results[site] = resolve_country_result(country_result)

# delv data
delv_key = {}
with open("body/MEGA.csv","r") as f:
    for line in f:
        terms = line.strip().split(',')
        rank = terms[0]
        site = terms[1]
        delv = terms[2]
        delv_key[site] = delv


# create lists for pandas dataframe
sites = []
ranks = []
tlds = []
tld_types = []
countries = []
delv_results = []
for site in sites_info:
    data = sites_info[site]
    sites.append(site)
    ranks.append(data[0])
    tlds.append(data[1])
    tld_types.append(data[2])
    if whois_results.get(site) != None: countries.append(whois_results[site])
    elif cctld_sites.get(site) != None: countries.append(cctld_sites[site])
    else: countries.append(None)
    delv_results.append(delv_key[site])

# make dataframe and save to csv
df = pd.DataFrame(data={"site":sites, "rank":ranks, "tld":tlds, "tld_type":tld_types, "country":countries, "delv_result":delv_results})
print(df)
df.to_csv('MASTER_RESULTS.csv',index=False)
