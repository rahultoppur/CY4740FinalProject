#!/usr/bin/python3

import os
from tranco import Tranco
import pandas as pd

with open("MASTER_RESULTS.csv","r") as f:
    for line in f:



# basic tranco data
contents = os.listdir('similarweb')
for c in contents:
    with open(f"similarweb/{c}","r") as f:
        for line in f:
            terms = line.strip().split(' ')
            rank = terms[0]
            site = terms[1]
            tld = site.split('.')[-1]
            tld_type = tld_types.get(tld)
            if tld_type == "ccTLD":
                cctld_sites[site] = country_cctlds[tld]
            sites_info[site] = [rank, tld, tld_type]
