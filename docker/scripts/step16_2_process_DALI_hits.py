#!/usr1/local/bin/python
import sys

dataset = sys.argv[1]
prot = sys.argv[2]

fp = open('step14_2/' + dataset + '/' + prot + '.dali', 'r')
HH_hits = []
for line in fp:
    words = line.split()
    ecod = words[0]
    score = float(words[1])
    resids = []
    for seg in words[2].split(','):
        if '-' in seg:
            start = int(seg.split('-')[0])
            end = int(seg.split('-')[1])
            for res in range(start, end + 1):
                resids.append(res)
        else:
            resids.append(int(seg))
    HH_hits.append([ecod, score, set(resids), words[2]])
fp.close()

HH_hits.sort(key = lambda x:x[1], reverse = True)
groups = []
for hit in HH_hits:
    hit_cov = hit[2]
    if not groups:
        groups.append([hit])
    else:
        for group in groups:
            for ghit in group:
                ghit_cov = ghit[2]
                overlap = hit_cov.intersection(ghit_cov)
                if len(overlap) > 0.2 * len(hit_cov) and len(overlap) > 0.2 * len(ghit_cov):
                    break
            else:
                group.append(hit)
                break
        else:
            groups.append([hit])

rp = open('step16_2/' + dataset + '/' + prot + '.result', 'w')
for count, group in enumerate(groups):
    rp.write('>group_' + str(count + 1) + '\n')
    for hit in group:
        rp.write(hit[0] + '\t' + str(hit[1]) + '\t' + hit[3] + '\n')
rp.close()
