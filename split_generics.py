#!/usr/bin/python3

# get CCTLDs
cctlds = []
with open("./whois/country-tlds","r") as f:
    for line in f:
        cctlds.append(line.strip())

# get 270k alrdy done
done = []
with open("./rahul-domains-clean","r") as f:
    for line in f:
        done.append(line.strip().split(',')[0])

new_csv = open("whois_remaining.csv","w")

# for site in tranco list
with open("./TRANCO_1m_MASTER.csv","r") as f:
    for line in f:
        rank, site = line.strip().split(',')
        tld = site.split('.')[-1]

        # if not in cctld AND if not in rahul's 270k alrdy done
        if tld not in cctlds and site not in done:
            # add to new csv
            new_csv.write(f"{rank},{site}\n")
