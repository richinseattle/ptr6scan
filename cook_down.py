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
from functools import wraps
import errno
import os
import signal
import re

queries=0
l=[]
progress=[0]*3
progressperc=0
gbase = ''

# abort function uppon exception, so no data is lost, or if the zone time-outs
# after two hours (unreasonably long)
def exit():
    print '#base %s, names found: %s, queries: %s' % (gbase, str(len(l)), str(queries))
    print '\n'.join(l)
    sys.exit(0)

class TimeoutError(Exception):
    pass

class timeout:
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message
    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)
    def __exit__(self, type, value, traceback):
        signal.alarm(0)


# attempt to perform a query
def tryquery(q, server):
    while 1:
        try:
            return query.udp(q, server, timeout=2)
        except KeyboardInterrupt:
            print >> sys.stderr, '\naborted, partial results follow'
            pass
        except SystemExit:
            sys.exit(0)
        except exception.Timeout:
            pass

def drilldown(base, server, limit, depth=0):
    global queries, l, progress, progressperc


    q = message.make_query(base, 'PTR')
    r = tryquery(q, server)
    queries = queries + 1

    # if we get no-error for this node, continue
    if r.rcode() == 0:
        # if we have reached the current depth limit, add base to the result set
        if len(base) == limit:
            l.append(base)
        # else if we have not yet reached the limit, continue on
        if len(base) < limit:
            # for all possible nibble values
            for c in '0123456789abcdef':
                # try to dig down recursively
                try:
                    drilldown(c+'.'+base, server, limit, depth+1)
                except SystemExit:
                    sys.exit(0)
                except KeyboardInterrupt:
                    print >> sys.stderr, '\naborted, partial results follow'
                    pass
                except TimeoutError:
                    print >> sys.stderr, 'timeout at: %s after %s queries' % (base, str(queries))
                    exit()
                    pass
                except:
                    print >> sys.stderr, 'error at: %s' % base
                    pass
            
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
        #print testbase
        cnt = cnt + test_base(testbase)
        #print cnt
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
if len(sys.argv) == 4:
    limit = int(sys.argv[3])/4*2+len('ip6.arpa.')
else:
    limit = 32*2+len('ip6.arpa.')


if base.endswith('ip6.arpa'):
    base = base + '.'

# set a global base to do correct error handling
gbase = base

if not base.endswith('ip6.arpa.'):
    print 'please pass an ip6.arpa name'
    sys.exit(1)

blacklist = check_blacklist(base)
if blacklist:
    print '#base %s appears to be blacklisted for being handled by "%s" after %s queries' % (base, blacklist ,str(queries))
    print >> sys.stderr, '#base %s appears to be blacklisted for being handled by "%s" after %s queries' % (base, blacklist ,str(queries))
    sys.exit(0)

if check_autogen(limit, base):
    print '#base %s appears to be autogenerated after %s queries' % (base, str(queries))
    print >> sys.stderr, '#base %s appears to be autogenerated after %s queries' % (base, str(queries))
    sys.exit(0)


with timeout(seconds=7200):
    try:
        if not len(base) >= limit:
            try:
                drilldown(base, server, limit)
            except SystemExit:
                sys.exit(0)
            except TimeoutError:
                print >> sys.stderr, 'timeout at: %s after %s queries' % (base, str(queries))
                exit()
                pass
            except KeyboardInterrupt:
                print >> sys.stderr, '\naborted, partial results follow'
                pass
            except:
                print >> sys.stderr, 'error at: %s' % base
                pass
        # if supplied base is already longer than the search-depth, crop to
        # length and add original+cropped base to output set
        else:
            l.append(base)
            if not len(base) == limit:
                l.append(base[(len(base)-limit):])
    except SystemExit:
        sys.exit(0)
    except KeyboardInterrupt:
        print >> sys.stderr, '\naborted, partial results follow'
        pass
    
exit()
