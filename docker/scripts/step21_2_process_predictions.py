#!/usr/bin/python
import numpy as np
import os, sys, json, math, string


def get_domain_range(resids):
    segs = []
    resids.sort()
    for resid in resids:
        if not segs:
            segs.append([resid])
        else:
            if resid > segs[-1][-1] + 1:
                segs.append([resid])
            else:
                segs[-1].append(resid)
    seg_string = []
    for seg in segs:
        start = str(seg[0])
        end = str(seg[-1])
        seg_string.append(start + '-' + end)
    return ','.join(seg_string)


def parse_domain(allresids, diso_resids, rpair2prob):
    chunks = []
    for x in range(0, len(allresids), 5):
        chunks.append(allresids[x : x + 5])

    segments_V0 = []
    for chunk in chunks:
        segment = []
        for res in chunk:
            if not res in diso_resids:
                segment.append(res)
        if len(segment) >= 3:
            segments_V0.append(segment)

    segment_probs = []
    spair2count = {}
    spair2total = {}
    for i, segi in enumerate(segments_V0):
        for j, segj in enumerate(segments_V0):
            if i < j:
                try:
                    spair2count[i]
                except KeyError:
                    spair2count[i] = {}
                try:
                    spair2total[i]
                except KeyError:
                    spair2total[i] = {}
                try:
                    spair2count[j]
                except KeyError:
                    spair2count[j] = {}
                try:
                    spair2total[j]
                except KeyError:
                    spair2total[j] = {}
                spair2count[i][j] = 0
                spair2total[i][j] = 0
                spair2count[j][i] = 0
                spair2total[j][i] = 0

                good = 0
                total = 0
                probs = []
                for resi in segi:
                    for resj in segj:
                        if resi + 5 < resj:
                            spair2count[i][j] += 1
                            spair2total[i][j] += rpair2prob[resi][resj]
                            spair2count[j][i] += 1
                            spair2total[j][i] += rpair2prob[resi][resj]
                            probs.append(rpair2prob[resi][resj])
                if probs:
                    meanprob = np.mean(probs)
                    if meanprob > 0.87:
                        segment_probs.append([i, j, meanprob])
    segment_probs.sort(key = lambda x:x[2], reverse = True)

    segments_V1 = []
    for item in segment_probs:
        segi = item[0]
        segj = item[1]
        if not segments_V1:
            segments_V1.append(set([segi, segj]))
        else:
            isdone = 0
            candidates = []
            for counts, segment in enumerate(segments_V1):
                if segi in segment and segj in segment:
                    isdone = 1
                elif segi in segment:
                    candidates.append(counts)
                elif segj in segment:
                    candidates.append(counts)

            if not isdone:
                if len(candidates) == 2:
                    c1 = candidates[0]
                    c2 = candidates[1]
                    intra_count1 = 0
                    intra_total1 = 0
                    intra_count2 = 0
                    intra_total2 = 0
                    inter_count = 0
                    inter_total = 0

                    for i in segments_V1[c1]:
                        for j in segments_V1[c1]:
                            if i < j:
                                intra_count1 += spair2count[i][j]
                                intra_total1 += spair2total[i][j]
                    for i in segments_V1[c2]:
                        for j in segments_V1[c2]:
                            if i < j:
                                intra_count2 += spair2count[i][j]
                                intra_total2 += spair2total[i][j]
                    for i in segments_V1[c1]:
                        for j in segments_V1[c2]:
                            inter_count += spair2count[i][j]
                            inter_total += spair2total[i][j]

                    merge = 0
                    intra_prob1 = intra_total1 / intra_count1
                    intra_prob2 = intra_total2 / intra_count2
                    inter_prob = inter_total / inter_count
                    if inter_prob * 1.15 >= intra_prob1 or inter_prob * 1.15 >= intra_prob2:
                        merge = 1

                    if merge:
                        new_segments = []
                        new_segment = set([])
                        for counts, segment in enumerate(segments_V1):
                            if counts in candidates:
                                new_segment = new_segment.union(segment)
                            else:
                                new_segments.append(segment)
                        new_segments.append(new_segment)
                        segments_V1 = new_segments
                    else:
                        pass

                elif len(candidates) == 1:
                    c0 = candidates[0]
                    intra_count = 0
                    intra_total = 0
                    inter_count = 0
                    inter_total = 0
                    for i in segments_V1[c0]:
                        for j in segments_V1[c0]:
                            if i < j:
                                intra_count += spair2count[i][j]
                                intra_total += spair2total[i][j]
                    if segi in segments_V1[c0]:
                        for k in segments_V1[c0]:
                            if segj != k:
                                inter_count += spair2count[k][segj]
                                inter_total += spair2total[k][segj]
                    elif segj in segments_V1[c0]:
                        for k in segments_V1[c0]:
                            if segi != k:
                                inter_count += spair2count[k][segi]
                                inter_total += spair2total[k][segi]
                    else:
                        print ('error0')

                    merge = 0
                    intra_prob = intra_total / intra_count
                    inter_prob = inter_total / inter_count
                    if inter_prob * 1.15 >= intra_prob:
                        merge = 1

                    if merge:
                        segments_V1[c0].add(segi)
                        segments_V1[c0].add(segj)
                    else:
                        pass

                elif len(candidates) == 0:
                    segments_V1.append(set([segi, segj]))
                else:
                    print ('error1')

    sorted_segments = []
    for item in segments_V1:
        resids = []
        for segind in item:
            for res in segments_V0[segind]:
                resids.append(res)
        resids.sort()
        if resids:
            sorted_segments.append([resids, np.mean(resids)])
    sorted_segments.sort(key = lambda x:x[1])
    domains = []    
    for item in sorted_segments:
        domains.append(item[0])
    return domains

dataset = sys.argv[1]
prot = sys.argv[2]
fp = open('step1/' + dataset + '/' + prot + '.fa', 'r')
protseq = ''
for line in fp:
    if line[0] != '>':
        protseq += line[:-1]
fp.close()
protlen = len(protseq)
RESIDS = list(range(1, protlen + 1))

DISO = set([])
fp = open('step13/' + dataset + '/' + prot + '.diso', 'r')
for line in fp:
    words = line.split()
    DISO.add(int(words[0]))
fp.close()

npz = np.load('step20_2/' + dataset + '/' + prot + '.npz', 'r')
preds = np.copy(npz['preds'])
if preds.shape[0] != protlen or preds.shape[1] != protlen:
    print ('error\t' + prot)
else:
    rpair2prob = {}
    for res1 in RESIDS:
        for res2 in RESIDS:
            try:
                rpair2prob[res1]
            except KeyError:
                rpair2prob[res1] = {}
            rpair2prob[res1][res2] = preds[res1 - 1, res2 - 1, 1]

    rp = open('step21_2/' + dataset + '/' + prot + '.result', 'w')
    domains = parse_domain(RESIDS, DISO, rpair2prob)
    for counti, domain in enumerate(domains):
        domain_range = get_domain_range(domain)
        rp.write('D' + str(counti) + '\t' + domain_range + '\n')
    rp.close()
