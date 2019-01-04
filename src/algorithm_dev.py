'''
Workspace to develop heartbeat detection algorithm
'''

import numpy as np
import matplotlib.pyplot as plt; plt.ion()

# load data
in_fname = '../data_example_hb.npy'
results = np.load(in_fname)

# results is (n_samples,3) numpy array
# 1st col: unix timestamp of sample
# 2nd col: value exported by duino
# 3rd col: ignore this for now
stamps = results[:,0]
data   = results[:,1]

# inspect the sampling rate
n_samples = stamps.size
n_secs = stamps[-1] - stamps[0]
sample_rate = n_samples / n_secs # Hz
print '{:d} samples in {:.02f} seconds ({:.02f} Hz)'.format(
    n_samples,n_secs,sample_rate)


# zoom in on a single heartbeat
beat = data[-1000:-900]

plt.plot(beat)
