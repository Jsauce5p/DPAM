#!/usr/bin/env python
import os, sys, time, subprocess
dataset = sys.argv[1]
ncore = sys.argv[2]
wd = os.getcwd()

for step in range(1,23):
    if step <= 13:
        if os.path.exists(dataset + '_step' + str(step) + '.log'):
            with open(dataset + '_step' + str(step) + '.log') as f:
                step_logs = f.read()
            if 'done\n' != step_logs:
                rcode = subprocess.run('run_step' + str(step) + '.py ' + dataset + ' ' + ncore,shell=True).returncode
                if rcode != 0:
                    print(f'Error in step{step}')
                    sys.exit()
        else:
            for s in range(step,23):
                os.system('rm ' + dataset + '_step' + str(s) + '.log')
                os.system('rm -rf step_' + str(s) + '/' + dataset + '/*')
            rcode = subprocess.run('run_step' + str(step) + '.py ' + dataset + ' ' + ncore,shell=True).returncode
            if rcode != 0:
                print(f'Error in step{step}')
                sys.exit()
    else:
        if os.path.exists(dataset + '_step' + str(step) + '_2.log'):
            with open(dataset + '_step' + str(step) + '_2.log') as f:
                step_logs = f.read()
            if 'done\n' != step_logs:
                rcode = subprocess.run('run_step' + str(step) + '_2.py ' + dataset + ' ' + ncore,shell=True).returncode
                if rcode != 0:
                    print(f'Error in step{step}_2')
                    sys.exit()
        else:
            for s in range(step,23):
                os.system('rm ' + dataset + '_step' + str(s) + '_2.log')
                os.system('rm -rf step_' + str(s) + '_2/' + dataset + '/*')
            rcode = subprocess.run('run_step' + str(step) + '_2.py ' + dataset + ' ' + ncore,shell=True).returncode
            if rcode != 0:
                print(f'Error in step{step}_2')
                sys.exit()
    
filelist = [wd + '/' + dataset + '_step' + str(k) + ('.log' if k <= 13 else '_2.log') for k in range(1, 23)]
undone = 22
for name in filelist:
    with open(name) as f:
        info = f.read()
    if info.strip() == 'done':
        undone = undone - 1
    else:
        print(dataset + ' ' + name.split('/')[-1].split(dataset + '_')[1]+' has errors..Fail')
        break
if undone == 0:
    print(dataset + ' done')
