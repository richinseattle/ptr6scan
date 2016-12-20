#!/usr/bin/python
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


import json
import sys
import re
import os



def arpa_to_addr(arpa):
    a = arpa.split('.')[:32]
    a.reverse()
    c = 0
    s = ""
    for i in a:
        s = s + i
        c = c + 1
        if c == 4 :
            s = s + ":"
            c = 0


    return s.strip(':')


print "graph v6 {"

data = {}

for l in sys.stdin:
    try:
        d = dict(json.loads(l.strip()))
        #if d['PTR'][:2] == "gw":
        s = '"'+":".join(arpa_to_addr(d['ARPA']).split(':')[:4])+'::/64" -- "'+d['PTR']+'" [style=""];'
        data[s] = {}
        s = '"'+d['PTR']+'" [label="", size=2, color=gray];'
        if data.has_key(s):
            data[s]['PFX'][":".join(arpa_to_addr(d['ARPA']).split(':')[:4])+'::/64'] = ""
        else:
            data[s] = {'PTR':d['PTR'],'PFX':{":".join(arpa_to_addr(d['ARPA']).split(':')[:4])+'::/64':""}}
        s = '"'+":".join(arpa_to_addr(d['ARPA']).split(':')[:4])+'::/64" [shape=box, color=blue];'
        data[s] = {}
        s = '"'+":".join(arpa_to_addr(d['ARPA']).split(':')[:4])+'::/64" -- "'+":".join(arpa_to_addr(d['ARPA']).split(':')[:3])+'::/48" [color=white];'
        data[s] = {}
        s = '"'+":".join(arpa_to_addr(d['ARPA']).split(':')[:3])+'::/48" [shape=box, color=red];'
        data[s] = {}
        s = '"'+":".join(arpa_to_addr(d['ARPA']).split(':')[:3])+'::/48" -- "'+":".join(arpa_to_addr(d['ARPA']).split(':')[:2])+'::/32" [color=white];'
        data[s] = {}
        s = '"'+":".join(arpa_to_addr(d['ARPA']).split(':')[:2])+'::/32" [shape=box, color=green];'
        data[s] = {}

        # this part may be flaky, hence commented out. When you want bigger
        # graphs, debug on your own :-)
        #s = '"'+":".join(arpa_to_addr(d['ARPA']).split(':')[:1])+'::/16" -- "'+":".join(arpa_to_addr(d['ARPA']).split(':')[:2])+'::/32";'
        #data[s] = {}
        #s = '"'+":".join(arpa_to_addr(d['ARPA']).split(':')[:1])+'::/16" [shape=box, color=gray];'
        #data[s] = {}
        #s = '"root" -> "'+":".join(arpa_to_addr(d['ARPA']).split(':')[:1])+'::/16";'
        data[s] = {}

    except:
        pass

for i in data.keys():
    
    if data[i].has_key('PFX'):
        if len(data[i]['PFX'].keys()) > 1:
            print >> sys.stderr, data[i]['PTR']+" is filled"
            print '"'+data[i]['PTR']+'" [label="", size=2, fillcolor = black, style = filled];'
        else:
            print i
    else:
        print >> sys.stderr, i

print "}"

