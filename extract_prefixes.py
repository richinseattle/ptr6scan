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

import sys
import os
import netaddr

# shorten .ip6.arpa. entry according to prefix length
def get_short(ipv6obj,mask):
    return ipv6obj.reverse_dns[(128-int(mask))/2:].strip('.')

# print ip6.arpa. zone for prefix
def print_unaligned(prefix, mask, short, ipv6obj):
    bits = 2**(4 - int(mask) % 4)
    char = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']
    last = char.index(get_short(ipv6obj, int(mask) + (4 - int(mask) % 4))[0])
    
    
    for i in range (last,bits+last):
        print char[i]+'.'+short

def print_prefix(prefix, mask):
    try:
        # try to transform prefix into an object readable by netaddr
        ipv6obj = ''
        if len(prefix.split(':')) > 8:
            ipv6obj = netaddr.IPAddress(prefix[:-1]+'0')
        elif not prefix[:-1] == ':':
            ipv6obj = netaddr.IPAddress(prefix)
        else:
            ipv6obj = netaddr.IPAddress(prefix+'0')
        short = get_short(ipv6obj, mask)
        print short
        # handle masks not % 4, i.e. not ending on nibble boundary
        if not int(mask) % 4 == 0:
            print_unaligned(prefix, mask, short, ipv6obj)
    except Exception, e:
        sys.stderr.write(i)
        sys.stderr.write(str(e))

# determin if the prefix is unicast, funny way due to $old netaddr versions on
# scientific linux
def check_net(ipnet):
    net = netaddr.IPNetwork(unicode(ipnet))
    if not (net.is_link_local() or net.is_loopback() or net.is_ipv4_compat() or net.is_ipv4_mapped() or net.is_private() or net.is_multicast() or net.is_reserved()):
        if net.prefixlen > 12:
            return ipnet
        else:
            return ""
    else:
        return ""

# check if prefix is unicast
def filter(line):
    items = line.split('|')
    ip = netaddr.IPNetwork(unicode(items[5]))
    if ip.version == 6:
        return check_net(items[5])
    else:
        return ""

# read list of prefixes from stdin until EOF
prefixes = []
for i in sys.stdin:
    prefix = filter(i.strip())
    if prefix:
        prefixes.append(prefix)

# for each prefix splitt off mask an process
for i in prefixes:
    prefix, mask = i.split('/')
    print_prefix(prefix, mask)
    
