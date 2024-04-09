#!/usr1/local/bin/python
import os, sys

dataset = sys.argv[1]
prot = sys.argv[2]
if os.path.exists('step11/' + dataset + '/' + prot + '.goodDomains'):
    rp1 = open('step14_2/' + dataset + '/'  + prot + '.hhs','w')
    rp2 = open('step14_2/' + dataset + '/'  + prot + '.dali','w')
    fp = open('step11/' + dataset + '/'  + prot + '.goodDomains','r')
    for line in fp:
        words = line.split()
        if words[0] == 'sequence':
            ecodnum = words[2].split('_')[0]
            prob = words[5]
            segments = words[8]
            rp1.write(ecodnum + '\t' + prob + '\t' + segments + '\n')
        elif words[0] == 'structure':
            ecodnum = words[4].split('_')[0]
            zscore = words[7]
            segments = words[14]
            rp2.write(ecodnum + '\t' + zscore + '\t' + segments + '\n')
    fp.close()
    rp1.close()
    rp2.close()
