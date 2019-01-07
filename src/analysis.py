
import sys, time
import numpy as np
import matplotlib.pyplot as plt


data_keys = {
     1: 'left - EO',
     2: 'left - EO',
     3: 'left - EO',
     4: 'left - EO',
     5: 'left - EO',
     6: 'down - EO',
     7: 'right - EO',
     8: 'up - EO',
     9: 'left - EC',
    10: 'down - EC',
}

try:
    data_num = int(sys.argv[-1])
except IndexError:
    raise Warning('must enter data value atm')

log_fname = './data{:02d}.log'.format(data_num)
val_fname = './data{:02d}.csv'.format(data_num)
plt_fname = './data{:02d}.png'.format(data_num)


# import logfile as a list of entries
with open(log_fname,'r') as infile:
    logs = infile.read().split('\n')

stamps, volts = np.loadtxt(val_fname,
                           skiprows=1,
                           delimiter=',',
                           dtype=[('stamps',float),
                                  ('volts',float)],
                           unpack=True)


# inspecting the sampling rate
n_samples = stamps.size
n_secs = stamps[-1] - stamps[0]
sample_rate = n_samples / n_secs # Hz
print '{:d} samples in {:.02f} seconds ({:.02f} Hz)'.format(
    n_samples,n_secs,sample_rate)


# grab timestamps of audio instructions
# (for now ignore directionality, all left)
# (for now ignore ms, bc not in struct_time)
soundtimes = [ x[:19] for x in logs if 'Played' in x ]
# convert them to unix, like the data timestamps
unxtimes = []
for s in soundtimes:
    tstruct = time.strptime(s,'%Y-%m-%d %H:%M:%S')
    unxtime = time.mktime(tstruct)
    unxtimes.append(unxtime)


# plot timecourse of when audio was playing
# and mark where audio started
# NOTE: there is a small but sig lag between
# when the audio "starts" and actually starts
LAG = 20 # secs
start_audio = unxtimes[0] - LAG
end_audio = unxtimes[-1] + LAG
audio_idx = np.logical_and(stamps>start_audio,
                           stamps<end_audio)


plt.plot(stamps[audio_idx],volts[audio_idx],c='k')
_ = [ plt.axvline(ut,c='r',ls='--') for ut in unxtimes ]
plt.title(data_keys[data_num])

plt.xlabel('Unix timestamp (s)')
plt.ylabel('Volts')

plt.savefig(plt_fname)
plt.show()