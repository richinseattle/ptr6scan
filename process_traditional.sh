#!/bin/bash
# Copyright (c) 2016, Tobias Fiebig
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies,
# either expressed or implied, of their employers.

set -u

### simple configuration
datadirectory='./data/'
TMPDIR='/tmp' # ideally use a ramfs for this;

# DNS Server to use; ideally utilize a local resolver
DNS='127.0.0.1'

# maximum number of parallel threads
PAR=80

# program paths: external
BGPDUMP='./bgpdump/bgpdump' # get it from https://bitbucket.org/ripencc/bgpdump/wiki/Home

# program paths: base system
SORT='/usr/bin/sort' # requires newer sort with --parallel
WGET='/usr/bin/wget'
CAT='/usr/bin/cat'
ZCAT='/usr/bin/zcat'
BZCAT='/usr/bin/bzcat'
CURL='/usr/bin/curl'
UNIQ='/usr/bin/uniq'
DATEPRG='/bin/date'
MV='/bin/mv'
PARALLEL='/usr/bin/parallel' # beware of this, older versions (EL6!) bloat the 
# tmp-folder by writing 8193 bytes to a file every N seconds; due to truncate
# semantics data is only appended -> disk full!

# program paths: internal
PRFXEXTRACT='./extract_prefixes.py'
COOKDOWN='./cook_down.py'
EXTRACTTERMINALS='./extract_terminals.py'

### advanced configuration

# Hosts from RIPE BGP collection
RIPEHOSTS="
rrc16
rrc15
rrc14
rrc13
rrc12
rrc11
rrc10
rrc09
rrc08
rrc07
rrc06
rrc05
rrc04
rrc03
rrc02
rrc01
rrc00
"

# RouteViews Route Collectors
rviews="
route-views.eqix
route-views.isc
route-views.kixp
route-views.jinx
route-views.linx
route-views.nwax
route-views.telxatl
route-views.wide
route-views.sydney
route-views.saopaulo
route-views.sg
route-views.perth
route-views.sfmix
route-views.soxrs
"

# determine current data for RouteViews format and obtain name of latest file
datem=`$DATEPRG +%Y.%m`
rviewslatest=`$CURL http://archive.routeviews.org/route-views.nwax/bgpdata/$datem/RIBS/ 2> /dev/null |grep -o -E '>(rib[^<]+)'|tail -n 1 | sed s/.//`

# determine indexing date
date=`$DATEPRG +%s`

# Prefix used for 
PRFX="$datadirectory/$date"


# create data storage directory
mkdir -p $PRFX

echo "obtaining raw data"

for i in $RIPEHOSTS; 
do 
	$WGET -o $PRFX/$i-gather.log -O $PRFX/$i.gz "http://data.ris.ripe.net/$i/latest-bview.gz";
done;

for i in $rviews; 
do
	$WGET -o $PRFX/$i-gather.log -O $PRFX/$i.bz2 "http://archive.routeviews.org/$i/bgpdata/$datem/RIBS/$rviewslatest";
done;

echo "decoding raw data"
for i in $PRFX/*.gz;
do
	$ZCAT $i | $BGPDUMP -m -v - > $i-plain;
done;

for i in $PRFX/*.bz2;
do
	$BZCAT $i | $BGPDUMP -m -v - > $i-plain;
done;

echo "extracting prefixes"
for i in $PRFX/*-plain;
do
	$CAT $i | $PRFXEXTRACT > $i-v6;
done;

echo "uniqing prefixes"
time $CAT $PRFX/*plain-v6 | $SORT --parallel=80 -S 32G | $UNIQ >  $PRFX/prefixes_uniq

echo "ip6.arpa." >> $PRFX/prefixes_uniq

echo "de-aggregating to /32"
time $CAT $PRFX/prefixes_uniq | $PARALLEL --linebuffer --tmpdir $TMPDIR -j $PAR "$COOKDOWN {} $DNS 32 " > $PRFX/32pref 2> $PRFX/32_run.log
echo "find-sort /32"
time $CAT $PRFX/32pref | grep -v '^#'  | $SORT --parallel=80 -S 32G |uniq > $PRFX/32agg

echo "de-aggregating to /48"
time $CAT $PRFX/32agg | $PARALLEL --linebuffer --tmpdir $TMPDIR -j $PAR "$COOKDOWN {} $DNS 48 " > $PRFX/48pref 2> $PRFX/48_run.log
echo "find-sort /48"
time $CAT $PRFX/48pref | grep -v '^#'  | $SORT --parallel=80 -S 32G |uniq > $PRFX/48agg

echo "de-aggregating to /64"
time $CAT $PRFX/48agg | $PARALLEL --linebuffer --tmpdir $TMPDIR -j $PAR "$COOKDOWN {} $DNS 64" > $PRFX/64pref 2> $PRFX/64_run.log
echo "find-sort /64"
time $CAT $PRFX/64pref | grep -v '^#'  | $SORT --parallel=80 -S 32G |uniq > $PRFX/64agg

echo "resolving hosts"
time $CAT $PRFX/64agg | grep -v '^#'  | $PARALLEL --linebuffer --tmpdir $TMPDIR -j $PAR "$EXTRACTTERMINALS {} $DNS $date" > $PRFX/dataset.json 2> $PRFX/terminal.log

$MV ./run.log $PRFX/run_log_full.log
