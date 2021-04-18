# `whois_fast`

A faster version than a linear implementation of `whois`.

## Main Idea
We first split up `top-1m.csv` the following way:
`split -l 10000 top-1m.csv -d -a 2 ''`

This will create files named `00`, `01`, `02`, ... each with 10000 lines of `top-1m.csv`. The intuition here is that each filename corresponds to a thread ID we spawn in our program.

In our script, we spawn `N` threads (identical to however many files we end up creating). The idea is that every thread will be responsible for reading input in from one file (say `00`), performing the `whois` query, and writing the responses (the countries for each domain) to `00-output`. 

The script assumes each input file is stored in a directory `input`. You also need to create a directory `output` where each output file will be written to. 

A similar idea can be applied when performing our `delv` queries as well.  

## To Run:
* Source the virtual environment: `source whois_fast/bin/activate`
* Run the script: `python3 whois_fast.py`

## Notes
Note that we need a small sleep (around `0.5` seconds) to "space-out" our queries to the `whois` database. Using the `whois` PyPi module is much quicker than subprocesses, since it uses sockets directly and avoids the associated overhead.
