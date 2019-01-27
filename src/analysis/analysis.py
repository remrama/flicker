
import time
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt


data_num = 1

log_fname = '../../data/data{:02d}.log'.format(data_num)
val_fname = '../../data/data{:02d}.csv'.format(data_num)
plt_fname = '../../data/data{:02d}.png'.format(data_num)


# import logfile as a list of entries
with open(log_fname,'r') as infile:
    logs = infile.read().split('\n')

# val_fname = '/Users/remy/Desktop/data.csv'
stamps, volts = np.loadtxt(val_fname,
                           skiprows=1,
                           delimiter=',',
                           dtype=[('stamps',float),
                                  ('volts',float)],
                           unpack=True)


# plot spectogram

def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    e_x = np.exp(x - np.max(x))
    return np.nan_to_num(e_x / np.nan_to_num(e_x.sum(axis=0)))

fs = 100. # sampling frequency in Hz
window_duration = 0.1 # seconds
window_samples = int(window_duration*fs)
sample_overlap = window_samples-1 # None is not the same as 0
window = 'boxcar'
f, t, Sxx = signal.spectrogram(volts,fs,window,window_samples,sample_overlap)
Sxx_soft = softmax(Sxx)

# max_frequency = 50 # for plotting in Hz
# plt.pcolormesh(t,f,Sxx_soft)
# plt.ylabel('Frequency [Hz]')
# plt.xlabel('Time [sec]')
# plt.ylim(0,max_frequency)

thresh = 0.999 # decoder output
target_freq_band = 1 # index
Sxx_thresh = Sxx_soft[target_freq_band,:]>=thresh

plt.plot(t,Sxx_thresh)
plt.plot(t,Sxx_soft[target_freq_band,:])
plt.ylabel('Detection')
plt.xlabel('Time [sec]')


# fs = 100. # sampling frequency in Hz
# window_duration = 0.1  #ssonds
# window_samples = int(window_duration*fs)
# sample_overlap = window_samples-1 # None is not the same as 0
# window = 'boxcar'
# f, t, Sxx = signal.spectrogram(volts,fs,window,window_samples,sample_overlap)
# Sxx_soft = softmax(Sxx)

# moving_avg_filter_duration = 1.0 # seconds 
# moving_avg_filter_len = fs*moving_avg_filter_duration
# filter_a = 1
# filter_b = np.ones(int(moving_avg_filter_len))/moving_avg_filter_len

# from scipy.signal import lfilter
# Sxx_target_filt = lfilter(filter_b,filter_a,Sxx_soft[target_freq_band,:])

# plt.plot(t,Sxx_target_filt)
# plt.ylabel('Detection')
# plt.xlabel('Time [sec]')



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


# # plot timecourse of when audio was playing
# # and mark where audio started
# # NOTE: there is a small but sig lag between
# # when the audio "starts" and actually starts
# LAG = 20 # secs
# start_audio = unxtimes[0] - LAG
# end_audio = unxtimes[-1] + LAG
# audio_idx = np.logical_and(stamps>start_audio,
#                            stamps<end_audio)

# plt.plot(stamps[audio_idx],volts[audio_idx],c='k')
# _ = [ plt.axvline(ut,c='r',ls='--') for ut in unxtimes ]
# plt.title(data_keys[data_num])

# plt.xlabel('Unix timestamp (s)')
# plt.ylabel('Volts')

# plt.savefig(plt_fname)
# plt.show()

