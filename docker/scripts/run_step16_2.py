#!/opt/conda/bin/python
import os, sys, subprocess

dataset = sys.argv[1]

if not os.path.exists('step16_2'):
    os.system('mkdir step16_2/')
if not os.path.exists('step16_2/' + dataset):
    os.system('mkdir step16_2/' + dataset)

fp = open(dataset + '_struc.list', 'r')
prots = []
for line in fp:
    words = line.split()
    prots.append(words[0])
fp.close()

need_prots = []
for prot in prots:
    if os.path.exists('step16_2/' + dataset + '/' + prot + '.result'):
        word_counts = set([])
        fp = open('step16_2/' + dataset + '/' + prot + '.result', 'r')
        for line in fp:
            words = line.split()
            word_counts.add(len(words))
        fp.close()
        if len(word_counts) == 1 and 21 in word_counts:
            pass
        else:
            os.system('rm step16_2/' + dataset + '/' + prot + '.result')
            need_prots.append(prot)
    elif os.path.exists('step16_2/' + dataset + '/' + prot + '.done'):
        pass
    else:
        need_prots.append(prot)


if need_prots:
    cmds = []
    for prot in need_prots:
        cmds.append('python /opt/DPAM/scripts/step16_2_process_DALI_hits.py ' + dataset + ' ' + prot)
    logs = batch_run(cmds, ncore)
    fail = [i for i in logs if 'fail' in i]
    if fail:
        with open(dataset + '_step16_2.log','w') as f:
            for i in fail:
                f.write(i+'\n')
    else:
        with open(dataset + '_step16_2.log','w') as f:
            f.write('done\n')
else:
    with open(dataset + '_step16_2.log','w') as f:
        f.write('done\n')
