#!/usr1/local/bin/python
import sys, random

dataset = sys.argv[1]
prot = sys.argv[2]

padlens = set([])
rp = open('step18_2/' + dataset + '/' + prot + '.results', 'w')
fp = open('step1/' + dataset + '/' + prot + '.fa', 'r')
protseq = ''
for line in fp:
    if line[0] != '>':
        protseq += line[:-1]
fp.close()
protlen = len(protseq)
if protlen <= 500:
    padlen = 500
elif protlen % 100 == 0:
    padlen = protlen
else:
    padlen = (protlen // 100) * 100 + 100
left = (padlen - protlen) // 2
right = padlen - protlen - left
rp.write(prot + '\t' + str(left) + '\t' + str(right) + '\t' + str(protlen) + '\t' + str(padlen) + '\n')
padlens.add(padlen)
rp.close()

padlens = list(padlens)
padlens.sort()
rp = open('step18_2/' + dataset + '/' + prot + '.list', 'w')
for padlen in padlens:
    rp.write(str(padlen) + '\n')
rp.close()
