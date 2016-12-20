# Summary

This toolchain allows the collection of datasets on assigned IPv6 reverse DNS
records. Furthermore, we include various tools for the subsequent analysis of
the obtained data. As this is academic code (read: horrific code quality, but
it works (for certain values of working)) we strongly advise everyone to
implement this **themself**. If you are unable to do so, you probably should not
play with this. :-)

## Publications

You can find a more in-depth description of this work in the following publication and talk:

**Something From Nothing (There): Collecting Global IPv6 Datasets From DNS**, *Tobias Fiebig, Kevin Borgolte, Shuang Hao, Christopher Kruegel, Giovanni Vigna*, accepted for PAM (Passiv and Active Measurement) Conference 2017, Sydney

**You can -j REJECT but you can not hide: Global scanning of the IPv6 Internet**, *Tobias Fiebig, Kevin Borgolte, Shuang Hao, Christopher Kruegel, Giovanni Vigna*, 33C3---33rd Chaos Communication Congress 2017, Hamburg

# Setup
The supplied tools are mostly ugly Python 2.6 and even more ugly shell. Please
give process.sh/process_traditional.sh a read and adjust the paths and variables
as they should be on your system.

# external tools

## GNU Parallel

This tooling heavily relies on GNU parallel. However, older versions may have
some unintended side-effects, filling up your disk, so make sure that you use
the newest versions.

## RIPE NCC bgpdump

For reading the seed BGP dumps we utilize a tool supplied by the RIPE NCC.
You can find it here: https://bitbucket.org/ripencc/bgpdump/wiki/Home


# Tool and File Description

## cook_down.py
Gets an .ip6.arpa. zone of any given length and then enumerates it up until
a certain length

Usage: 
```
./cook_down.py $ip6.arpa_zone $DNS_Server $desired_length
```

## extract_terminals.py
Similar to cook_down.py, but resolves to terminal records. Prints JSON formated
output.

Usage:
```
extract_terminals.py $ip6.arpa_zone $DNS_Server $numeric_experiment_identifier
```

## process.sh
Main processing script. Implements 4 nibble wide breadth-first steps. 
Read the script before running it! 

## process_traditional.sh
Similar to process.sh, but using the initial step-sizes (32 -> 48 -> 64 -> 128).


## run.sh
Convenient envelop script handling a little bit of output.

## extract_prefixes.py
Script used to test for valid unicast IPv6 prefixes from bgpdump.

## prexclude
Blacklist for ip6.arpa zones; see file for an example.

## filter.py
Small script reading JSON as in the output files from stdin, outputting a more
readable (and scanable) form.

## dot.py
Funny tool eating output JSON from stdin, building a .dot graph description file
for stdout with errors on stderr. Best visualized with Gephi. (https://gephi.org/)
Beware: This code just barely works, and is extremly ugly.

# Licence
The supplied tools are provided under a 2-clause BSD licence; Please see the
individual files for the specific licence.
