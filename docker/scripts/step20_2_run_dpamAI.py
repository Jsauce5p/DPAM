#!/usr1/local/bin/python
import os, sys, random
import numpy as np
import tensorflow as tf
from datetime import datetime

mygpu = '0' # 0,1,2,3,4,5,6,7
os.environ['CUDA_VISIBLE_DEVICES'] = mygpu
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)

dataset = sys.argv[1]
prot = sys.argv[2]
fp = open('step18_2/' + dataset + '/' + prot + '.list', 'r')
totallens = []
for line in fp:
    words = line.split()
    totallens.append(int(words[0]))
fp.close()

len2slices = {}
for totallen in totallens:
    len2slices[totallen] = []
    fp = open('step19_2/' + dataset + '/' + str(totallen) + '.slices', 'r')
    for line in fp:
        myslice = []
        for word in line[:-1].split(','):
            start = word.split('-')[0]
            end = word.split('-')[1]
            myslice.append([start, end])
        len2slices[totallen].append(myslice)
    fp.close()

all_prots = []
prot2left = {}
prot2right = {}
prot2len = {}
prot2slices = {}
prot2count = {}
fp = open('step18_2/' + dataset + '/' + prot + '.results','r')
for line in fp:
    words = line.split()
    prot = words[0]
    length = int(words[4])
    all_prots.append(prot)
    prot2left[prot] = int(words[1])
    prot2right[prot] = int(words[2])
    prot2len[prot] = length
    prot2slices[prot] = len2slices[length]
    prot2count[prot] = len(prot2slices[prot])
fp.close()

def load_data(prot, dataset):
    length = prot2len[prot]
    left = prot2left[prot]
    right = prot2right[prot]
    npz = np.load('step17_2/' + dataset + '/' + prot + '.npz')
    raw_inputs = np.copy(npz['inputs'])
    raw_mask = np.copy(npz['mask'])
    raw_labels = np.copy(npz['labels'])
    inputs = np.zeros((length, length, 24), dtype = np.float32)
    mask = np.zeros((length, length), dtype = np.bool)
    labels = np.zeros((length, length), dtype = np.int32)
    if right:
        inputs[left:-right, left:-right, :] = raw_inputs
        mask[left:-right, left:-right] = raw_mask
        labels[left:-right, left:-right] = raw_labels
    else:
        inputs[left:, left:, :] = raw_inputs
        mask[left:, left:] = raw_mask
        labels[left:, left:] = raw_labels
    return [inputs, mask, labels]

def get_feed(prot, allinputs, allmask, alllabels, myslice):
    inputs = np.zeros((1, 500, 500, 24), dtype = np.float16)
    mask = np.zeros((1, 500, 500), dtype = np.bool)
    labels = np.zeros((1, 500, 500), dtype = np.int8)

    if len(myslice) == 1:
        start = myslice[0][0]
        end = myslice[0][1]
        inputs[0, :, :, :24] = allinputs[int(start):int(end), int(start):int(end), :24]
        mask[0, :, :] = allmask[int(start):int(end), int(start):int(end)]
        labels[0, :, :] = alllabels[int(start):int(end), int(start):int(end)]

    elif len(myslice) == 2:
        start1 = myslice[0][0]
        end1 = myslice[0][1]
        len1 = int(end1) - int(start1)
        start2 = myslice[1][0]
        end2 = myslice[1][1]
        inputs[0, :len1, :len1, :] = allinputs[int(start1):int(end1), int(start1):int(end1), :]
        inputs[0, len1:, len1:, :] = allinputs[int(start2):int(end2), int(start2):int(end2), :]
        inputs[0, :len1, len1:, :] = allinputs[int(start1):int(end1), int(start2):int(end2), :]
        inputs[0, len1:, :len1, :] = allinputs[int(start2):int(end2), int(start1):int(end1), :]
        mask[0, :len1, :len1] = allmask[int(start1):int(end1), int(start1):int(end1)]
        mask[0, len1:, len1:] = allmask[int(start2):int(end2), int(start2):int(end2)]
        mask[0, :len1, len1:] = allmask[int(start1):int(end1), int(start2):int(end2)]
        mask[0, len1:, :len1] = allmask[int(start2):int(end2), int(start1):int(end1)]
        labels[0, :len1, :len1] = alllabels[int(start1):int(end1), int(start1):int(end1)]
        labels[0, len1:, len1:] = alllabels[int(start2):int(end2), int(start2):int(end2)]
        labels[0, :len1, len1:] = alllabels[int(start1):int(end1), int(start2):int(end2)]
        labels[0, len1:, :len1] = alllabels[int(start2):int(end2), int(start1):int(end1)]
    
    feed_dict = {'myinputs': inputs, 'mymask': mask, 'mylabels': labels}
    return feed_dict


model = tf.keras.models.load_model('/opt/DPAM/scripts/dpamAI_weights')
layer_name = 'tf.nn.softmax'
intermediate_layer_model = tf.keras.Model(inputs = model.input, outputs = model.get_layer(layer_name).output)

for prot in all_prots:
    length = prot2len[prot]
    left = prot2left[prot]
    right = prot2right[prot]
    allcounts = np.zeros((length, length, 2), dtype = np.int32)
    allpreds = np.zeros((length, length, 2), dtype = np.float32)
    [allinputs, allmask, alllabels] = load_data(prot, dataset)

    for myslice in prot2slices[prot]:
        feed_dict = get_feed(prot, allinputs, allmask, alllabels, myslice)
        feed_dict['mymask'] = np.expand_dims(feed_dict['mymask'],axis=-1)
        feed_dict['mylabels'] = np.expand_dims(feed_dict['mylabels'],axis=-1)
        input_array = np.concatenate((feed_dict['myinputs'],feed_dict['mymask'],feed_dict['mylabels']), axis=-1)
        labels = feed_dict['mylabels']
        mypreds = intermediate_layer_model.predict(x=input_array)
        if len(myslice) == 1:
            start = myslice[0][0]
            end = myslice[0][1]
            allcounts[int(start):int(end), int(start):int(end), :] += 1
            allpreds[int(start):int(end), int(start):int(end), :] += mypreds[0, :, :, :]
        elif len(myslice) == 2:
            start1 = myslice[0][0]
            end1 = myslice[0][1]
            len1 = int(end1) - int(start1)
            start2 = myslice[1][0]
            end2 = myslice[1][1]
            allcounts[int(start1):int(end1), int(start1):int(end1), :] += 1
            allcounts[int(start2):int(end2), int(start2):int(end2), :] += 1
            allcounts[int(start1):int(end1), int(start2):int(end2), :] += 1
            allcounts[int(start2):int(end2), int(start1):int(end1), :] += 1
            allpreds[int(start1):int(end1), int(start1):int(end1), :] += mypreds[0, :len1, :len1, :]
            allpreds[int(start2):int(end2), int(start2):int(end2), :] += mypreds[0, len1:, len1:, :]
            allpreds[int(start1):int(end1), int(start2):int(end2), :] += mypreds[0, :len1, len1:, :]
            allpreds[int(start2):int(end2), int(start1):int(end1), :] += mypreds[0, len1:, :len1, :]
        else:
            print ('error', prot, myslice)

    if right:
        newcounts = allcounts[left:-right, left:-right, :]
        newpreds = allpreds[left:-right, left:-right, :]
    else:
        newcounts = allcounts[left:, left:, :]
        newpreds = allpreds[left:, left:, :]
    avepreds = newpreds / newcounts
    np.savez_compressed('step20_2/' + dataset + '/' + prot + '.npz', preds = avepreds)
