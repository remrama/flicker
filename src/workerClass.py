"""
See class docs.
"""
import serial
import numpy as np
import pyqtgraph as pg
from copy import copy
from collections import deque

from detectorClass import myDetector


class myWorker(pg.QtCore.QObject):
    """
    Collects data from Arduino, or simulates data
    if no Arduino is found during initialization.
    Operates on its own thread (see runall.py).

    Data is saved directly from this QObject,
    but is also passed to myWindow via QT
    signals/slots for plotting and event logging.

    Various options/buttons from the GUI (<myWindow>) 
    are passed here via QT signals/slots.

    All main parameters are controlled from the 
    config file, and passed through during runall.py
    <myDetector> is opened as an attribute here,
    so the parameters for that are passed from runall.py
    into here as well.
    """

    ## initialize the QT signals that will be sent out to <myWindow>
    ## (they get sent out whenever their "emit()" attribute is called)
    # data for <myWindow> to plot (volts,stamps,pollstamps)
    signal4plot = pg.QtCore.pyqtSignal(deque,deque,deque)
    # message for <myWindow> to display and save to log file
    # (there's only an occasional need for this)
    signal4log = pg.QtCore.pyqtSignal(str,bool,float)
    # data for PSD visualization
    signal4psdplot = pg.QtCore.pyqtSignal(list)

    def __init__(self,serial_name,              # of Arduino
                      data_buffer_len,          # n datapoints to keep in buffer
                      max_analog_volts,         # for volts conversion
                      analog_read_resolution,   # for volts conversion (unique to Teensy)
                      internal_sampling_rate_hz,# passed to detector
                      moving_average_secs,      # passed to detector
                      psd_calc_window_secs,     # passed to detector
                      target_freq_index,        # passed to detector, 2nd lowest freq recorded
                      detection_threshold_up,   # passed to detector
                      detection_threshold_down, # passed to detector
                      lrlr_window_secs,         # secs that n peaks must occur within for detection
                      n_peaks_for_lrlr_detection, # n peaks required to trigger detection
                      data_fname,
                      saving):

        super(self.__class__,self).__init__()


        self.SERIAL_NAME = serial_name
        self.DATA_BUFFER_LEN = data_buffer_len
        self.MAX_ANALOG_VOLTS = max_analog_volts
        self.ANALOG_READ_RESOLUTION = analog_read_resolution
        self.LRLR_WINDOW_SECS = lrlr_window_secs
        self.N_PEAKS_FOR_LRLR_DETECTION = n_peaks_for_lrlr_detection
        self.DATA_FNAME = data_fname
        self.SAVING = saving

        self.COLUMNS = ['timestamp','volts'] # of data output file

        # initialize empty lists for holding data/time buffers
        self.data = deque(maxlen=self.DATA_BUFFER_LEN)
        self.stamps = deque(maxlen=self.DATA_BUFFER_LEN)
        self.pollstamps = deque(maxlen=self.DATA_BUFFER_LEN)
        ## TEMP just hvae pollstamps for testing
        ## to distinguish poll vs data incoming frequency

        # empty deque to hold detected flicks,
        # to help detect 4 consecutive flicks (1 LRLR)
        self.lrlr = deque(maxlen=4)

        self.gain = 1 # start here, modulated from window slider

        # initialize detector
        self.detector = myDetector(internal_sampling_rate_hz,
                                   moving_average_secs,
                                   psd_calc_window_secs,
                                   target_freq_index,
                                   detection_threshold_up,
                                   detection_threshold_down)


    def keep_grabbingData_and_checking4flick(self):
        """
        Called during thread initialization (see runall.py).
        Loops over
            - grabbing data from Arduino
            - send data (and more) to <myWindow>
            - check for LRLR detection
        """

        # send one-time intialization message to <myWindow>
        self.signal4log.emit('App started',False,0)

        # open connection or simulate data on fail
        self._connect2arduino()

        # open new file with column names
        self._startNewFile()

        while True: # run until GUI closes

            # pull from Arduino or simulate data
            if self.duino:
                volt = self._grabData()
            else:
                volt = self._generateSimulatedData()

            # collect a timestamp for this datapoint
            stamp = serial.time.time()

            # save a stamp to reflect the polling rate, even if not data returned
            self.pollstamps.append(stamp)        

            if volt: # sometimes Arduino doesn't send anything and so volts will be None
                
                # update data and stamp buffers
                self.data.append(volt)
                self.stamps.append(stamp)

                # send them to <myWindow> where they will be plotted and saved
                self.signal4plot.emit(copy(self.stamps),
                                      copy(self.data),
                                      copy(self.pollstamps))
                ## TODO: better route than making copies?
                ## issue was that plot would fail early,
                ## i think bc "views" were being passed and deques would change
                ## ie, after x was plotted, y would have a new value appended.
                ## Could also init deques with 1000 zeros. dont like that either.

                # check for LRLR series (skip beginning of stream)
                if len(self.data) >= self.DATA_BUFFER_LEN:
                    self._check4lrlr()

                # save to file
                if self.SAVING:
                    self._saverow(rowlist=[stamp,volt])

            # wait a bit bc that makes it work :/
            serial.time.sleep(.001)


    def _check4lrlr(self):
        """
        Look for <n_peaks_for_lrlr_detection>, and
        trigger event if a LRLR is found.

        Uses <myDetector> which checks for single peaks/flicks,
        and keeps timestamps of the most recent peaks and checks
        if <lrlr_window_secs> has passed between them.
        """
        # first check for a single flick/peak (ie, not a LRLR series)
        self.detector.update_status(list(self.data),list(self.stamps),self.gain)
        # if a peak, add to the running list of peaks
        if self.detector.status == 'rising':
            print 'rising'
            # add the most recent timestamp indicating the time of detection
            self.lrlr.append(self.stamps[-1])
            # check if the timepassed between all 4 is within range
            if len(self.lrlr)==self.N_PEAKS_FOR_LRLR_DETECTION \
            and self.lrlr[-1]-self.lrlr[0] < self.LRLR_WINDOW_SECS:
                # send message to display, with most recent x value for plotting
                self.signal4log.emit('Flick detected',False,self.stamps[-1])
                # clear the flick record, preventing rapid consecutive detections
                self.lrlr.clear()
                # # send to duino if wanna trigger something
                # if self.duino is not None:
                #     self.duino.write(bytes(1))


    def _connect2arduino(self):
        """
        Try to open serial connection to Arduino
        and start data simulation if fails.
        """
        try:
            ## TODO: add timeout and baudrate args
            self.duino = serial.Serial(self.SERIAL_NAME)
        except serial.serialutil.SerialException:
            self.duino = None
            self.signal4log.emit('No serial connection, simulating data',True,0)
            self.initializeSimulation()

    def _raw2volts(self,x):
        '''for conversion of sensor output to volts'''
        return self.MAX_ANALOG_VOLTS * x / float(2**self.ANALOG_READ_RESOLUTION)

    def _volts2raw(self,x):
        return x * 2**self.ANALOG_READ_RESOLUTION / float(self.MAX_ANALOG_VOLTS)

    def _startNewFile(self):
        '''initializes file with column names only'''
        with open(self.DATA_FNAME,'w') as newfile:
            newfile.write(','.join(self.COLUMNS))

    def _saverow(self,rowlist):
        '''Appends existing file.
        ARGS
        ----
        rowlist : 1 value for each column
        '''
        with open(self.DATA_FNAME,'a') as outfile:
            outfile.write('\n'+','.join([ str(x) for x in rowlist ]))

    # @pg.QtCore.pyqtSlot(int) # maybe not necessary
    def update_gain(self,new_gain):
        """
        Signal comes from <myWindow>
        """
        self.gain = new_gain

    def _grabData(self):
        """
        Grab single value from Arduino and convert to volts.

        TODO
        Currently this only returns the last value, even
        if multiple values come through serial at once.
        """
        # receive from serial
        str_vals = self.duino.readline()
        # sometimes 2 vals get sent
        list_str_vals = str_vals.split('\r')
        rawvals = [ float(x) for x in list_str_vals if x.isalnum() ]
        # sometimes Arduino sends nothing so make sure there is at least 1 value
        if len(rawvals) > 0:
            volts = self.__raw2volts(rawvals[-1])
            return volts

    def _generateSimulatedData(self):
        """
        Act as the Arduino/grabData() by simulating a single volts value.
        """
        if len(self.stamps)>1:
            time_passed = self.stamps[-1]-self.stamps[-2]
        else:
            time_passed = None
        high_freq_noise = np.random.normal(0,self.high_freq_noise_var)
        med_freq_noise = self.med_freq_noise(np.random.normal(0,self.med_freq_noise_var),time_passed)
        low_freq_noise = self.low_freq_noise(np.random.normal(0,self.low_freq_noise_var),time_passed)
        signal = self.get_total_signal()
        noise = self.baseline_voltage+high_freq_noise+med_freq_noise+low_freq_noise
        volt = signal + noise
        return volt

    def get_total_signal(self):
        total_signal = 0
        for signal in self.signals:
            total_signal += self.get_sinusoid_signal(signal)
            if self.stamps[-1]-signal['start_time']>=signal['duration']:
                self.signals.remove(signal)
        return total_signal

    def get_sinusoid_signal(self, signal):
        t    = self.stamps[-1]-signal['start_time']
        mag  = signal['magnitude']
        freq = 2*np.pi/float(signal['duration'])
        return 0.5*mag*(1-np.cos(freq*t))

    def initializeSimulation(self):
        self.baseline_voltage = 0.07
        self.high_freq_noise_var = 0.001
        self.med_freq_noise_var = 0.05
        self.low_freq_noise_var = 0.1
        self.med_freq_noise_cutoff = 0.4 # Hz
        self.low_freq_noise_cutoff = 0.03 # Hz
        self.med_freq_noise = LowPassFilter(cutoff=self.med_freq_noise_cutoff)
        self.low_freq_noise = LowPassFilter(cutoff=self.low_freq_noise_cutoff)

        self.signals = []
        self.signal_duration_range = [0.06, 0.18] # seconds
        self.signal_magnitude_range = [0.03, 0.05] # volts

    def generateSignal(self,generate):
        '''Hackey but <generate> is a bool that will be sent
        as True to start this function
        '''
        duration = np.random.uniform(self.signal_duration_range[0],self.signal_duration_range[1])
        magnitude = np.random.uniform(self.signal_magnitude_range[0],self.signal_magnitude_range[1])
        self.signals.append({'duration':duration,
                             'magnitude':magnitude,
                             'start_time':self.stamps[-1]})

class LowPassFilter(object):

    def __init__(self, cutoff, freq=100):
        self.__freq = freq
        self.__cutoff = cutoff
        self.__setAlpha()
        self.__y = self.__s = None

    def __setAlpha(self):
        te    = 1.0 / self.__freq
        tau   = 1.0 / (2*np.pi*self.__cutoff)
        alpha =  1.0 / (1.0 + tau/te)
        if alpha<=0 or alpha>1.0:
            raise ValueError("alpha (%s) should be in (0.0, 1.0]"%alpha)
        self.__alpha = alpha

    def __call__(self, value, time_passed=None):        
        if time_passed is not None:
            self.__freq = 1.0 / float(time_passed)
            self.__setAlpha()
        if self.__y is None:
            s = value
        else:
            s = self.__alpha*value + (1.0-self.__alpha)*self.__s
        self.__y = value
        self.__s = s
        return s

    def lastValue(self):
        return self.__y