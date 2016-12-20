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

import os
import sys
import re
import json

import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LogNorm
from numpy import arange
from scipy.interpolate import spline
from pylab import *

def plot(x,y,z):
    fig = plt.figure(1, figsize = (10,4),frameon=True)
    ax = plt.subplot(111)
    
    plt.scatter(y,x,c=z,marker="s",s=140,norm=LogNorm(vmin=0.01, vmax=1),cmap=plt.cm.Blues)

    plt.yticks(np.arange(0,16,1), ("0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f"))
    plt.xticks(np.arange(1,32,4), ("/0","/16","/32","/48","/64","/80","/96","/112","8","9","a","b","c","d","e","f"))
    plt.ylim((-1,16))
    plt.xlim((0,33))

    cb = plt.colorbar()
    cb.set_label('Frequency of Nibble Value$_{log}$')
    plt.xlabel("IPv6 Address Prefix Size")
    plt.ylabel("Nibble Value")

    
    ax.xaxis.labelpad = -1
    ax.xaxis.grid(True, linestyle='-', which='major', color='grey',alpha=0.5)
    plt.savefig('./v6.pdf',dpi = (250),format='pdf')


def get_data(str_file):
    cc = 0
    ret = {}
    records = 0
    for i in range(1,33):
        ret[i] = {}
        for j in "0123456789abcdef":
            ret[i][int(j,16)] = 0.0
    f = open(str_file)
    for l in f:
        try:
            d = json.loads(l.strip())
            l = d['ARPA']
        except:
            pass
        addr = []
        try:
            addr = l.split('.')
            if len(addr) == 35:
                addr = addr[:32]
            else:
                addr = []
        except:
            pass
        c = 32
        for i in addr:
            if c == 32:
                cc = cc + 1
            ret[c][int(i,16)] = ret[c][int(i,16)] + 1.0
            c = c - 1
        records = records + 1

    print ""
    x = []
    y = []
    z = []
    print ret
    for i in ret.keys():
        for j in ret[i].keys():
            if ret[i][j] > 0:
                y.append(i)
                x.append(j)
                z.append(ret[i][j] / records)
    print ""
    return x, y, z



x,y,z = get_data('./input')
plot(x,y,z)
