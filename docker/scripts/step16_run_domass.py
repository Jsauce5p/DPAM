#!/opt/conda/bin/python
import os
import sys
import numpy as np
import tensorflow as tf

dataset = sys.argv[1]
local_device_protos = tf.config.list_physical_devices('GPU')
if not local_device_protos:
    print("No GPUs found. Falling back to CPU.")
    # In TensorFlow 2.x, GPU configurations are handled differently and often
    # may not need explicit handling for many cases.
else:
    # TensorFlow 2.x automatically handles GPU allocation. To limit GPU memory
    # or enable memory growth, use tf.config.experimental.set_memory_growth
    for gpu in local_device_protos:
        tf.config.experimental.set_memory_growth(gpu, True)

fp = open('step16_' + dataset + '.list', 'r')
prots = [line.split()[0] for line in fp]
fp.close()

all_cases = []
all_inputs = []
for prot in prots:
    data_path = f'step15/{dataset}/{prot}.data'
    if os.path.exists(data_path):
        with open(data_path, 'r') as fp:
            for countl, line in enumerate(fp):
                if countl:
                    words = line.split()
                    all_cases.append([prot, *words[0:5], *words[17:23]])
                    all_inputs.append([float(word) for word in words[4:17]])
total_case = len(all_cases)

def get_feed(batch_inputs):
    inputs = np.zeros((100, 13), dtype=np.float32)
    for i, batch_input in enumerate(batch_inputs):
        inputs[i, :len(batch_input)] = batch_input
    return inputs

model = tf.keras.Sequential([
    tf.keras.layers.InputLayer(input_shape=(13,)),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(2, activation='softmax')
])

# Replace with your model's load path
model.load_weights('/mnt/databases/domass_epo29')

all_preds = []
if total_case >= 100:
    for i in range(0, total_case, 100):
        batch_inputs = all_inputs[i:i+100]
        batch_preds = model.predict(get_feed(batch_inputs))
        all_preds.extend(batch_preds)

        if i % 1000 == 0:
            print(f'prediction for batch {i // 100}')
else:
    fold = 100 // total_case + 1
    pseudo_inputs = all_inputs * fold
    batch_inputs = pseudo_inputs[:100]
    batch_preds = model.predict(get_feed(batch_inputs))
    all_preds.extend(batch_preds[:total_case])

prot2results = {prot: [] for prot in prots}
for i, (this_case, this_input) in enumerate(zip(all_cases, all_inputs)):
    this_pred = all_preds[i]
    prot = this_case[0]
    prot2results[prot].append([*this_case[1:5], this_pred[1], *this_input[3:13], *this_case[5:]])

for prot in prots:
    result_path = f'step16/{dataset}/{prot}.result'
    if prot2results[prot]:
        with open(result_path, 'w') as rp:
            header = 'Domain\tRange\tTgroup\tECOD_ref\tDPAM_prob\tHH_prob\tHH_cov\tHH_rank\tDALI_zscore\tDALI_qscore\tDALI_ztile\tDALI_qtile\tDALI_rank\tConsensus_diff\tConsensus_cov\tHH_hit\tDALI_hit\tDALI_rot1\tDALI_rot2\tDALI_rot3\tDALI_trans\n'
            rp.write(header)
            for item in prot2results[prot]:
                rp.write('\t'.join(str(x) for x in item) + '\n')
    else:
        os.system(f'echo \'done\' > step16/{dataset}/{prot}.done')
