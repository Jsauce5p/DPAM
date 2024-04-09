#!/usr/bin/python
import sys
import os

def get_dist(CA1, CA2, coors1, coors2):
	dist = ((CA1[0] - CA2[0]) ** 2 + (CA1[1] - CA2[1]) ** 2 + (CA1[2] - CA2[2]) ** 2) ** 0.5
	if dist < 20:
		dists = []
		for coor1 in coors1:
			for coor2 in coors2:
				dist = ((coor1[0] - coor2[0]) ** 2 + (coor1[1] - coor2[1]) ** 2 + (coor1[2] - coor2[2]) ** 2) ** 0.5
				dists.append(dist)
		mindist = min(dists)
	else:
		mindist = 20
	return mindist


dataset = sys.argv[1]
prot = sys.argv[2]
domains = []
fp = open('/home/s438180/example/step21_2/' + dataset + '/' + prot + '.result','r')
for line in fp:
    words = line.split()
    domains.append([words[0], words[1]])
fp.close()

fp = open('/home/s438180/example/step2/' + dataset + '/' + prot + '.pdb','r')
all_resids = set([])
resid2coors = {}
resid2CA = {}
for line in fp:
	if len(line) >= 50:
		if line[:4] == 'ATOM':
			resid = int(line[22:26])
			coorx = float(line[30:38])
			coory = float(line[38:46])
			coorz = float(line[46:54])
			atomtype = line[13:17].strip()
			all_resids.add(resid)
			if atomtype == 'CA':
				resid2CA[resid] = [coorx, coory, coorz]
			try:
				resid2coors[resid].append([coorx, coory, coorz])
			except KeyError:
				resid2coors[resid] = [[coorx, coory, coorz]]
fp.close()

min_resid = min(all_resids)
max_resid = max(all_resids)


new_domains = []
for item in domains:
	domid = item[0]
	segs = item[1].split(',')
	new_segs = []

	dom_resids = set([])
	for seg in segs:
		if '-' in seg:
			start = int(seg.split('-')[0])
			end = int(seg.split('-')[1])
			dom_resids = dom_resids.union(set(range(start, end + 1)))
		else:
			dom_resids.add(int(seg))
	other_resids = all_resids.difference(dom_resids)

	for seg in segs:
		left_resids = []
		right_resids = []
		if '-' in seg:
			start = int(seg.split('-')[0])
			end = int(seg.split('-')[1])
			seg_resids = set(range(start, end + 1))
			for res in range(start, end + 1):
				left_resids.append(res)
				right_resids.insert(0, res)
		else:
			seg_resids = set([int(seg)])
			left_resids.append(int(seg))
			right_resids.append(int(seg))

		bad_resids = set([])
		for focus_res in left_resids:
			intra_contacts = []
			inter_contacts = []
			for res in dom_resids:
				if focus_res - res > 6 or focus_res - res < -6:
					mindist = get_dist(resid2CA[focus_res], resid2CA[res], resid2coors[focus_res],  resid2coors[res])
					if mindist < 6:
						intra_contacts.append(res)
			for res in other_resids:
				if focus_res - res > 6 or focus_res - res < -6:
					mindist = get_dist(resid2CA[focus_res], resid2CA[res], resid2coors[focus_res],  resid2coors[res])
					if mindist < 6:
						inter_contacts.append(res)
			intra_count = len(intra_contacts)
			inter_count = len(inter_contacts)
			if not intra_count:
				bad_resids.add(focus_res)
			elif inter_count > intra_count:
				bad_resids.add(focus_res)
			else:
				break

		for focus_res in right_resids:
			intra_contacts = []
			inter_contacts = []
			for res in dom_resids:
				if focus_res - res > 6 or focus_res - res < -6:
					mindist = get_dist(resid2CA[focus_res], resid2CA[res], resid2coors[focus_res],  resid2coors[res])
					if mindist < 6:
						intra_contacts.append(res)
			for res in other_resids:
				if focus_res - res > 6 or focus_res - res < -6:
					mindist = get_dist(resid2CA[focus_res], resid2CA[res], resid2coors[focus_res],  resid2coors[res])
					if mindist < 6:
						inter_contacts.append(res)
			intra_count = len(intra_contacts)
			inter_count = len(inter_contacts)
			if not intra_count:
				bad_resids.add(focus_res)
			elif inter_count > intra_count:
				bad_resids.add(focus_res)
			else:
				break

		newseg_resids = seg_resids.difference(bad_resids)
		if newseg_resids:
			new_start = min(newseg_resids)
			new_end = max(newseg_resids)
			new_segs.append(str(new_start) + '-' + str(new_end))
	if new_segs:
		new_domains.append([domid, ','.join(new_segs)])


get_resids = set([])
for item in new_domains:
	segs = item[1].split(',')
	for seg in segs:
		if '-' in seg:
			start = int(seg.split('-')[0])
			end = int(seg.split('-')[1])
			get_resids = get_resids.union(set(range(start, end + 1)))
		else:
			get_resids.add(int(seg))

final_domains = []
for item in new_domains:
	domid = item[0]
	segs = item[1].split(',')
	new_segs = []

	dom_resids = set([])
	for seg in segs:
		if '-' in seg:
			start = int(seg.split('-')[0])
			end = int(seg.split('-')[1])
			dom_resids = dom_resids.union(set(range(start, end + 1)))
		else:
			dom_resids.add(int(seg))
	other_resids = all_resids.difference(dom_resids)

	for seg in segs:
		left_resids = []
		right_resids = []
		if '-' in seg:
			start = int(seg.split('-')[0])
			end = int(seg.split('-')[1])
			seg_resids = set(range(start, end + 1))
			for i in range(1, 21):
				if end + i in get_resids:
					break
				if end + i <= max_resid:
					right_resids.append(end + i)
			for i in range(1, 21):
				if start - i in get_resids:
					break
				if start - i >= min_resid:
					left_resids.append(start - i)
		else:
			resid = int(seg)
			seg_resids = set([resid])
			for i in range(1, 21):
				if resid + i in get_resids:
					break
				if resid + i <= max_resid:
					right_resids.append(resid + i)
			for i in range(1, 21):
				if resid - i in get_resids:
					break
				if resid - i >= min_resid:
					left_resids.append(resid - i)

		add_resids = set([])
		for focus_res in left_resids:
			intra_contacts = []
			inter_contacts = []
			for res in dom_resids:
				if focus_res - res > 6 or focus_res - res < -6:
					mindist = get_dist(resid2CA[focus_res], resid2CA[res], resid2coors[focus_res],  resid2coors[res])
					if mindist < 6:
						intra_contacts.append(res)
			for res in other_resids:
				if focus_res - res > 6 or focus_res - res < -6:
					mindist = get_dist(resid2CA[focus_res], resid2CA[res], resid2coors[focus_res],  resid2coors[res])
					if mindist < 6:
						inter_contacts.append(res)
			intra_count = len(intra_contacts)
			inter_count = len(inter_contacts)
			if intra_count > inter_count:
				add_resids.add(focus_res)
			else:
				break

		for focus_res in right_resids:
			intra_contacts = []
			inter_contacts = []
			for res in dom_resids:
				if focus_res - res > 6 or focus_res - res < -6:
					mindist = get_dist(resid2CA[focus_res], resid2CA[res], resid2coors[focus_res],  resid2coors[res])
					if mindist < 6:
						intra_contacts.append(res)
			for res in other_resids:
				if focus_res - res > 6 or focus_res - res < -6:
					mindist = get_dist(resid2CA[focus_res], resid2CA[res], resid2coors[focus_res],  resid2coors[res])
					if mindist < 6:
						inter_contacts.append(res)
			intra_count = len(intra_contacts)
			inter_count = len(inter_contacts)
			if intra_count > inter_count:
				add_resids.add(focus_res)
			else:
				break

		newseg_resids = seg_resids.union(add_resids)
		if newseg_resids:
			new_start = min(newseg_resids)
			new_end = max(newseg_resids)
			if not new_segs:
				new_segs.append([new_start, new_end])
			else:
				if new_start > new_segs[-1][-1] + 1:
					new_segs.append([new_start, new_end])
				else:
					new_segs[-1][-1] = new_end
	if new_segs:
		final_segs = []
		for seg in new_segs:
			final_segs.append(str(seg[0]) + '-' + str(seg[1]))
		final_domains.append([domid, ','.join(final_segs)])

if os.path.exists('/home/s438180/example/' + dataset + '_domains'):
	sump = open(dataset + '_domains', 'a')
	for item in final_domains:
		sump.write(prot + '\t' + item[0] + '\t' + item[1] + '\n')
else:
	sump = open('/home/s438180/example/'+ dataset + '_domains', 'w')
	sump.write('Protein\tDomain\tRange\n')
	for item in final_domains:
		sump.write(prot + '\t' + item[0] + '\t' + item[1] + '\n')

rp = open('/home/s438180/example/step22_2/' + dataset + '/' + prot + '.result','w')
for item in final_domains:
    rp.write(item[0] + '\t' + item[1] + '\n')
rp.close()
