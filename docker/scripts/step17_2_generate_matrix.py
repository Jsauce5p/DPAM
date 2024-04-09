#!/usr1/local/bin/python
import numpy as np
import os, sys, json, math, string


dataset = sys.argv[1]
prot = sys.argv[2]

fp = open('/home/s438180/test_ecod_dpam_ai/step1/' + dataset + '/' + prot + '.fa', 'r')
protseq = ''
for line in fp:
    if line[0] != '>':
        protseq += line[:-1]
fp.close()
protlen = len(protseq)
    
pos1_mtx = np.zeros((protlen, protlen), dtype = np.float32)
pos2_mtx = np.zeros((protlen, protlen), dtype = np.float32)
for i in range(protlen):
    pos1_mtx[:,i] = (i + 1) / 100
    pos2_mtx[i,:] = (i + 1) / 100


dist_mtx = np.zeros((protlen, protlen), dtype = np.float32)
fp = open('/home/s438180/test_ecod_dpam_ai/step2/' + dataset + '/' + prot + '.pdb','r')
resid2coors = {}
resids = []
for line in fp:
    resid = int(line[22:26])
    coorx = float(line[30:38])
    coory = float(line[38:46])
    coorz = float(line[46:54])
    atomtype = line[13:17].strip()
    try:
        resid2coors[resid].append([coorx, coory, coorz])
    except KeyError:
        resid2coors[resid] = [[coorx, coory, coorz]]
        resids.append(resid)
fp.close()

for res1 in resids:
    for res2 in resids:
        if res1 < res2:
            dists = []
            for coor1 in resid2coors[res1]:
                for coor2 in resid2coors[res2]:
                    dist = ((coor1[0] - coor2[0]) ** 2 + (coor1[1] - coor2[1]) ** 2 + (coor1[2] - coor2[2]) ** 2) ** 0.5
                    dists.append(dist)
            mindist = min(dists)
            dist_mtx[res1 - 1, res2 - 1] = mindist / 50
            dist_mtx[res2 - 1, res1 - 1] = mindist / 50


pae_mtx = np.zeros((protlen, protlen), dtype = np.float32)
fp = open('/home/s438180/test_ecod_dpam_ai/' + dataset + '/' + prot + '.json','r')
text = fp.read()[1:-1]
fp.close()
json_dict = json.loads(text)
pae_mtx[:,:] = json_dict['predicted_aligned_error']
pae_mtx /= 100



hhs_mtx = np.zeros((protlen, protlen, 10), dtype = np.float32)
fp = open('/home/s438180/test_ecod_dpam_ai/step15_2/' + dataset + '/' + prot + '.result', 'r')
all_hits = []
group_num = 0
hits = []
for line in fp: # combine all the hits into a single list
    if line[0] == '>':
        if group_num and hits:
            if group_num <= 10:
                all_hits.append(hits)
        group_num = int(line[1:-1].split('_')[1])
        hits = []
    else:
        words = line.split()
        hits.append(words)
if group_num and hits:
    if group_num <= 10:
        all_hits.append(hits)
fp.close()

for i, hits in enumerate(all_hits): # query each group of hits and keep running count

    for hit in hits: # query each hit within group of hits
        score = float(hit[1]) # set score for hit
        resids = []
        for seg in hit[2].split(','): # get residues covered in hit
            if '-' in seg:
                start = int(seg.split('-')[0])
                end = int(seg.split('-')[1])
                for res in range(start, end + 1): # append all covered residues to list
                    resids.append(res)
            else:
                resids.append(int(seg)) # append if its a single residue
        for res1 in resids: # for each position on the grid replace the zero with the normalized score
            for res2 in resids:
                if score > hhs_mtx[res1 - 1, res2 - 1, i]:
                    hhs_mtx[res1 - 1, res2 - 1, i] = score / 50



dali_mtx = np.zeros((protlen, protlen, 10), dtype = np.float32)
fp = open('/home/s438180/test_ecod_dpam_ai/step16_2/' + dataset + '/' + prot + '.result', 'r')
all_hits = []
group_num = 0
hits = []
for line in fp:
    if line[0] == '>':
        if group_num and hits:
            if group_num <= 10:
                all_hits.append(hits)
        group_num = int(line[1:-1].split('_')[1])
        hits = []
    else:
        words = line.split()
        hits.append(words)
if group_num and hits:
    if group_num <= 10:
        all_hits.append(hits)
fp.close()

for i, hits in enumerate(all_hits):
    for hit in hits:
        score = float(hit[1])
        resids = []
        for seg in hit[2].split(','):
            if '-' in seg:
                start = int(seg.split('-')[0])
                end = int(seg.split('-')[1])
                for res in range(start, end + 1):
                    resids.append(res)
            else:
                resids.append(int(seg))
        for res1 in resids:
            for res2 in resids:
                if score > dali_mtx[res1 - 1, res2 - 1, i]:
                    dali_mtx[res1 - 1, res2 - 1, i] = score / 10


mask_mtx = np.zeros((protlen, protlen), dtype = bool)
ecod_mtx = np.zeros((protlen, protlen), dtype = np.int8)



all_mtx = np.zeros((protlen, protlen, 24), dtype = np.float32)
all_mtx[:,:,0] = dist_mtx
all_mtx[:,:,1] = pae_mtx
all_mtx[:,:,2] = pos1_mtx
all_mtx[:,:,3] = pos2_mtx
all_mtx[:,:,4:14] = hhs_mtx
all_mtx[:,:,14:24] = dali_mtx
np.savez_compressed('/home/s438180/test_ecod_dpam_ai/step17_2/' + dataset + '/' + prot + '.npz', inputs = all_mtx, mask = mask_mtx, labels = ecod_mtx)
