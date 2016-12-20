#!/usr/bin/env python
# Copyright (c) 2016, Peter van Dijk, Tobias Fiebig
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

from dns import message, query, exception
import sys
import json
import hashlib
import re
import logging


DEBUG = False

queries=0
results = 0
l=[]
index_data = []
progress=[0]*3
progressperc=0
cont = False
autogen = False
runid = 0


# obtain more interesting data from a DNS query
def parse_to_dict(r):
    d = str(r)
    ret = {'error':False,'runid':runid}
    for i in d.split(';'):
        cur = i.split('\n')
        if len(cur) > 1:
            try:
                if not cur[0][0] == 'i':
                    ret[cur[0]] = cur[1]
                    if cur[0] == 'ANSWER':
                        ret['PTR'] = ''
                        ret['CNAME'] = ''
                        ptrdata = cur[1].split(' ')
                        if ptrdata[-2] == 'PTR':
                            ret['PTR'] = ptrdata[-1]
                        else:
                            ret['CNAME'] = ptrdata[-1]
                else:
                    iddict = {}
                    for j in cur:
                        if j:
                            idlist = j.split(' ')
                            iddict[idlist[0]] = ' '.join(idlist[1:])
                    ret['metadata'] = iddict
            except:
                ret['data'] = d
                ret['error'] = True
        elif not cur:
            ret[cur[0]] = ''
    return ret

def tryquery(q, server):
    rt = 0
    while True:
        try:
            return query.udp(q, server, timeout=2)
        except exception.Timeout:
            rt = rt + 1

# here for historic reasons; used to write to a DB
def store(dict_data):
    global index_data, queries, autogen
    if not dict_data['PTR']:
        dict_data['PTR'] = 'EMPTY TERMINAL POSSIBLE CNAME'
    if DEBUG:
        print dict_data
    print json.dumps(dict_data)


def drilldown(base, server, limit, depth=0):
    global queries, l, progress, progressperc, cont, results, autogen

    q = message.make_query(base, 'PTR')
    r = tryquery(q, server)
    queries = queries + 1

    if r.rcode() == 0:
        if len(base) == limit:
            d = parse_to_dict(r)
            d['ARPA'] = base
            store(d)
            results = results + 1
        if len(base) < limit:
             for c in '0123456789abcdef':
                if depth < len(progress):
                    progress[depth]=int(c, 16)
                drilldown(c+'.'+base, server, limit, depth+1)

def test_base(base):
    global queries
    q = message.make_query(base, 'PTR')
    r = tryquery(q, server)
    queries = queries + 1
    if r.rcode() == 0:
        return 1
    else:
        return 0

def check_autogen(limit, base):
    add_length = (limit - len(base)) / 2
    if add_length < 4:
        return False
    cnt = 0
    for c in '0123456789abcdef':
        testbase = add_length * (c+".") + base
        cnt = cnt + test_base(testbase)
    if cnt >= 3:
        return True
    else:
        return False

def check_blacklist(base):
    for line in open('./prexclude'):
        name, regex = line.strip().split(';')
        r = re.compile(regex)
        if r.findall(base):
            return name
    return ""


(base, server) = sys.argv[1:3]

limit = 73
runid = int(sys.argv[3])


if base.endswith('ip6.arpa'):
    base = base + '.'

if not base.endswith('ip6.arpa.'):
    print >> sys.stderr, 'please pass an ip6.arpa name'
    sys.exit(1)

blacklist = check_blacklist(base)
if blacklist:
    print >> sys.stderr, '#base %s appears to be blacklisted for being handled by "%s" after %s queries' % (base, blacklist ,str(queries))
    sys.exit(0)

if check_autogen(limit, base):
    print >> sys.stderr, '#base %s appears to be autogenerated after %s queries' % (base, str(queries))
    sys.exit(0)

try:
    drilldown(base, server, limit)
except KeyboardInterrupt:
    print >> sys.stderr, '\naborted, partial results follow'
except:
    pass


print >> sys.stderr, 'base: %s, queries done: %s, names found: %s' % (base, queries, results)
