import numpy as np
from scipy.signal import welch

class myDetector(object):
    def __init__(self, internal_sampling_rate_hz, # in Hz
            moving_average_secs, # in sec
            psd_calc_window_secs, # in sec
            target_freq_index, # the second lowest frequency recorded
            detection_threshold_up,
            detection_threshold_down):
        # load and interpret constants
        self.INTERNAL_SAMPLING_RATE_HZ = float(internal_sampling_rate_hz)
        self.MOVING_AVERAGE_FRAMES = int(moving_average_secs*self.INTERNAL_SAMPLING_RATE_HZ)
        self.PSD_CALC_WINDOW_SECS = float(psd_calc_window_secs)
        self.PSD_WINDOW_FRAMES = int(self.INTERNAL_SAMPLING_RATE_HZ*self.PSD_CALC_WINDOW_SECS)
        self.TARGET_FREQ_INDEX = int(target_freq_index) # literally the [0,1,...,N] index of frequency band, should be changed

        # state
        self.status = 'idle' # 'rising', 'ongoing', 'falling', 'idle'
        self.target_frequency_band_history = np.zeros(self.MOVING_AVERAGE_FRAMES)
        self.current_frequency_band_activity = 0

        # thresholds for detection
        self.DETECTION_THRESHOLD_UP = detection_threshold_up  # arbitrary (>D_T_D)
        self.DETECTION_THRESHOLD_DOWN = detection_threshold_down # arbitrary (<=D_T_U)

    def update_status(self, volts_in_history, unix_timestamps, gain):
        assert np.shape(volts_in_history) == np.shape(unix_timestamps) # should be same length
        # time_history = np.cumsum(np.diff(unix_timestamps)) # convert unixtime to current time
        time_history = np.array(unix_timestamps) - unix_timestamps[0] # convert unixtime to current time
        volts_in_history = volts_in_history[::-1] # I think this needs to be reversed as done here? depends on input order
        resampled_time = np.arange(0, self.PSD_CALC_WINDOW_SECS, 1/self.INTERNAL_SAMPLING_RATE_HZ)
        assert len(resampled_time) == self.PSD_WINDOW_FRAMES # must be same for filtering to work
        resampled_volts_history = gain*np.interp(resampled_time, time_history, volts_in_history)
        [sampled_freqs, signal_psd] = welch(resampled_volts_history, fs=self.INTERNAL_SAMPLING_RATE_HZ, window='boxcar', nperseg=self.PSD_WINDOW_FRAMES) #, noverlap=0)
        softmax_signal_psd = softmax(signal_psd)
        target_signal_psd = softmax_signal_psd[self.TARGET_FREQ_INDEX]
        self.target_frequency_band_history = np.roll(self.target_frequency_band_history, 1)
        self.target_frequency_band_history[0] = target_signal_psd 
        self.current_frequency_band_activity = np.mean(self.target_frequency_band_history) # moving average filter
        # could add extra conditions here to detect single frame differences, but should be OK
        if self.status == 'idle' and self.current_frequency_band_activity > self.DETECTION_THRESHOLD_UP:
            self.status = 'rising'
        elif self.status == 'rising':
            self.status = 'ongoing'
        elif self.status == 'ongoing' and self.current_frequency_band_activity < self.DETECTION_THRESHOLD_DOWN:
            self.status = 'falling'
        elif self.status == 'falling':
            self.status = 'idle'

        return self.status, softmax_signal_psd

def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    e_x = np.exp(x - np.max(x))
    return np.nan_to_num(e_x / np.nan_to_num(e_x.sum(axis=0)))