#!/usr1/local/bin/python
import sys, random

dataset = sys.argv[1]
prot = sys.argv[2]

def get_slice(padlen):
    slices = []
    if padlen > 500:
        bin100 = padlen // 100
        bin200 = padlen // 200
        bin300 = padlen // 300
        bin400 = padlen // 400
        for i in range(bin100):
            start1 = i * 100
            end1 = start1 + 100
            for j in range(bin400):
                start2 = end1 + j * 400
                end2 = start2 + 400
                if end2 <= padlen:
                    if start2 == end1:
                        slices.append([[start1, end2]])
                    else:
                        slices.append([[start1, end1], [start2, end2]])

        for i in range(bin200):
            start1 = i * 200
            end1 = start1 + 200
            for j in range(bin300):
                start2 = end1 + j * 300
                end2 = start2 + 300
                if end2 <= padlen:
                    if start2 == end1:
                        slices.append([[start1, end2]])
                    else:
                        slices.append([[start1, end1], [start2, end2]])

        for i in range(bin300):
            start1 = i * 300
            end1 = start1 + 300
            for j in range(bin200):
                start2 = end1 + j * 200
                end2 = start2 + 200
                if end2 <= padlen:
                    if start2 == end1:
                        slices.append([[start1, end2]])
                    else:
                        slices.append([[start1, end1], [start2, end2]])

        for i in range(bin400):
            start1 = i * 400
            end1 = start1 + 400
            for j in range(bin100):
                start2 = end1 + j * 100
                end2 = start2 + 100
                if end2 <= padlen:
                    if start2 == end1:
                        slices.append([[start1, end2]])
                    else:
                        slices.append([[start1, end1], [start2, end2]])
    else:
        slices.append([[0, 500]])
    return slices


fp = open('step18_2/' + dataset + '/' + prot + '.list', 'r')
for line in fp:
    padlen = int(line)
    slices = get_slice(padlen)
    results = set([])
    for item in slices:
        segments = []
        for segment in item:
            start = segment[0]
            end = segment[1]
            segments.append(str(start) + '-' + str(end))
        results.add(','.join(segments))
    rp = open('step19_2/' + dataset + '/' +str(padlen) + '.slices', 'w')
    for result in results:
        rp.write(result + '\n')
    rp.close()
