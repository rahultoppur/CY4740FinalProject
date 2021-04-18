# Types of TLDs
- infrastructure top-level domain (ARPA)
- generic top-level domains (gTLD)
- generic-restricted top-level domains (grTLD)
- sponsored top-level domains (sTLD)
- country code top-level domains (ccTLD)
- test top-level domains (tTLD)

# Key
- country-tlds:
  - ccTLD
- generic-tlds:
  - gTLD
  - sTLD
  - grTLD
- odd-tlds:
  - "infrastructure" (ARPA)
- error-tlds:
  - appears to be all tlds that were non-latin characters
  - with the exception of "onion"

# TLD Takeaways
- generic-tlds sites will need whois info
- we should consider whether we want to analyze error-tlds and odd-tlds or not

# whois Trial Results:
- Out of Tranco 1M:
  - sites that need whois: 677233
  - sites that don't need whois: 321625
- Out of 2000 trial sites:
  - success count: 1533
  - none count: 467
  - took about an hour to do 2000 sites oof (on my dinky laptop, to be fair)
- Out of ~500 generic TLDs:
  -

# whois Notes
- whois country results are NOT standardized
- most use country codes, but some country codes are lowercase/not standardized/not countries at all
  - i.e. UK, which is not the country code for Great Britain (GB), but also not for the only other reasonable option, Ukraine (UA)
  - some are formatted like "Great Britain (UK)"
  - some just use the country name itself, but there's no way to ensure these are standardized necessarily
  - some have stuff like "null", "REDACTED FOR PRIVACY", "Statutory Masking Enabled"
  - some have either just a number (i.e. 108-8001) or a number and country code (i.e. 89/IT)
- sometimes you just get a whois error i.e. "whois: whois.primalstore.com: nodename nor servname provided, or not known: Invalid argument"
- getting whois results takes forever and we would need a way of putting timeouts on each query
- not all generic TLDs are guaranteed to give country info in whois:
  - 

# whois Takeaways
- country codes should work for most whois results but we will likely need to create a list of country result exceptions and manually map each exception to the correct country code and then systematically update the dataframe for each exception
- we need to implement whois query timeouts to speed up the process
- we need to use multithreading
- we should retry errored sites at the end just to give a second chance
- cooloff period, too many queries
- grep for just country

# Sources
- TLD types pulled from [wikipedia](https://en.wikipedia.org/wiki/List_of_Internet_top-level_domains#Types)
- TLD list csv files (basic and detailed) downloaded from [here](https://tld-list.com/free-downloads)
- ccTLD country csv pulled from [here](https://gist.github.com/derlin/421d2bb55018a1538271227ff6b1299d#file-country-codes-tlds-csv)
- Country information csv including country codes and ccTLDs pulled form [here](https://www.ip2location.com/free/country-information)
