#!/usr/bin/env python3

import whois
import logging
import threading
import time

logging.basicConfig(level=logging.DEBUG)

NUM_THREADS = 2 # use argparse here later...

# Perform a whois query to get the country for a domain
def issue_whois(domain):
    try:
        query = whois.query(domain)
    except Exception as e:
        #logging.error(e) # need to log this
        return f"{domain},None"

    # Search for the country in the query response
    if query.registrant_country:
        logging.debug(f"{domain},{query.registrant_country}")
        return f"{domain},{query.registrant_country}"
    else:
        logging.debug(f"{domain},None")
        return f"{domain},None"
        #return domain + ',' + re.findall(r'\bAdmin Country:\s+\w+|\bRegistrant Country:\s+\w+', query.text)[0].split(':')[-1]

# Get the domains from the given input file 
def read_input(filename):
    with open(f"./input/{filename}", 'r') as fd:
        domains = []
        for line in fd:
            domains.append(line.strip().split(',')[-1])
    return domains

# Perform a whois query on each domain, write to a file
def write_output(filename):
    with open(f"./output/{filename}-output", 'w') as fd:
        domains = read_input(filename)
        for d in domains:
            time.sleep(0.5)
            fd.write(f"{issue_whois(d)}\n")


if __name__ == '__main__':
    threads = []
    for i in range(NUM_THREADS):
        t = threading.Thread(target=write_output, args=(i,))
        threads.append(t)

    # Start each thread
    for t in threads:
        t.start()
        logging.debug(f"thread {i} started")

    # Join our threads
    for t in threads:
        t.join()


