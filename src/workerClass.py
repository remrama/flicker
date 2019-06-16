
from collections import deque

import serial
import numpy as np
import pyqtgraph as pg
from copy import copy

from detectorClass import myDetector




class myWorker(pg.QtCore.QObject):
    '''
    Collect data using a QObject so that it can
    be placed on a QThread and run in the background.
    Also saves data if told to.
    '''

    # signal gets sent to the plotter with each "emit" call
    signal4plot = pg.QtCore.pyqtSignal(deque,deque,deque)
    # signal gets sent to event list if signal detected
    signal4log = pg.QtCore.pyqtSignal(str,bool,float)
    # signal goes to psdplotter for visualization only
    signal4psdplot = pg.QtCore.pyqtSignal(list)

    def __init__(self,serial_name='/dev/cu.usbmodem53254001',
                      buffer_len=1000,
                      fname='../data/temp.csv',
                      columns=['stamp','data'],
                      max_analog_volts=3.3,
                      analog_read_resolution=13,
                      internal_sampling_rate=100,   # passed to detector
                      moving_average_time=1.0,      # passed to detector
                      psd_calc_window_time=0.1,     # passed to detector
                      target_freq_index=1,          # passed to detector
                      detection_threshold_up=0.6,   # passed to detector
                      detection_threshold_down=0.4, # passed to detector
                      saving=False):

        super(self.__class__,self).__init__()


        self.NAME = serial_name
        self.BUFFER_LEN = buffer_len
        self.SAVING = saving
        self.FNAME = fname
        self.COLUMNS = columns
        self.MAX_ANALOG_VOLTS = max_analog_volts
        self.ANALOG_READ_RESOLUTION = analog_read_resolution


        # connect to serial
        try: # try to intialize connection with duino
            ## TODO: add timeout and baudrate args
            self.duino = serial.Serial(self.NAME)
        except serial.serialutil.SerialException:
            self.duino = None
            self.initializeSimulation()

        # initialize empty lists for holding data/time buffers
        self.data = deque(maxlen=self.BUFFER_LEN)
        self.stamps = deque(maxlen=self.BUFFER_LEN)
        self.pollstamps = deque(maxlen=self.BUFFER_LEN)
        ## TEMP just hvae pollstamps for testing
        ## to distinguish poll vs data incoming frequency

        self.gain = 1 # start here, modulated from window slider

        # initialize detector
        self.detector = myDetector(internal_sampling_rate,
                                   moving_average_time,
                                   psd_calc_window_time,
                                   target_freq_index,
                                   detection_threshold_up,
                                   detection_threshold_down)

        self._startNewFile()


    def _raw2volts(self,x):
        '''for conversion of sensor output to volts'''
        return self.MAX_ANALOG_VOLTS * x / float(2**self.ANALOG_READ_RESOLUTION)

    def _volts2raw(self,x):
        return x * 2**self.ANALOG_READ_RESOLUTION / float(self.MAX_ANALOG_VOLTS)

    def _startNewFile(self):
        '''initializes file with column names only'''
        with open(self.FNAME,'w') as newfile:
            newfile.write(','.join(self.COLUMNS))

    def _saverow(self,rowlist):
        '''Appends existing file.
        ARGS
        ----
        rowlist : 1 value for each column
        '''
        with open(self.FNAME,'a') as outfile:
            outfile.write('\n'+','.join([ str(x) for x in rowlist ]))

    # @pg.QtCore.pyqtSlot(int) # maybe not necessary
    def update_gain(self,new_gain):
        self.gain = new_gain
        print(self.gain)

    def check4flick(self):
        '''Look for signal in data passed in.
        '''
        # # grab a subset of data buffer
        # data2search = list(islice(reversed(self.data),0,self.buffer_len)) # ugly slice bc of deque
        # data2search = self.data # WHOLE THING
        status, psdvals = self.detector.update_status(list(self.data),list(self.stamps),self.gain)
        
        # send psd to plot widget, even if not currently open
        self.signal4psdplot.emit(list(psdvals))

        # handle flick
        if status == 'rising':
            # log_and_display(win,'Flick detected')
            # send to duino
            # win.myThread.msleep(100)
            # duino.write(bytes(1))
            # time.sleep(1)

            # send to duino
            if self.duino is not None:
                self.duino.write(bytes(1))
            # send message to display, with most recent x value for plotting
            self.signal4log.emit('Flick detected',False,self.stamps[-1])

        # elif self.duino is None:
        #     # give a random simulate flick signal
        #     if np.random.uniform() > .99:
        #         self.signal4log.emit('Flick detected',False,self.stamps[-1])


    def keepGrabbingData(self):
        '''This is the function called to start thread.'''
        # send some intro log messages
        self.signal4log.emit('App started',False,0)
        if self.duino is None:
            self.signal4log.emit('No serial connection, simulating data',True,0)
        while True:
            self.grabData()
            serial.time.sleep(.001)

    def grabData(self):
        '''
        Grab data from the teensy by checking serial port.
        This includes the emit() method, which automatically
        sends its args to wherever it is latter 'connected'.
        Doesn't return anything, just appends to buffers.
        '''
        try:
            # receive from serial
            ser_str = self.duino.readline()
            # sometimes 2 vals get sent
            sep = ser_str.split('\r')
            vals = [ float(x) for x in sep if x.isalnum() ]
        except AttributeError: # since duino is None-type if no duino
            # simulate serial
            vals = [self._volts2raw(self.generateSimulatedData())] # as list to match receive_serial output
        stamp = serial.time.time()

        ## TODO: currently this only includes the last
        ## _if_ multiple values come thru serial at once
        if len(vals) > 0:
            v = self._raw2volts(vals[-1])
            # update data buffer
            self.data.append(v)
            self.stamps.append(stamp)
            self.pollstamps.append(stamp)
            # save
            if self.SAVING:
                self._saverow(rowlist=[stamp,v])
        else:
            # log_and_display('Serial poll came back empty')
            self.pollstamps.append(stamp)
        # send signal to wherever it gets connected to
        self.signal4plot.emit(copy(self.stamps),copy(self.data),copy(self.pollstamps))
        
        # check for saccade
        # skip beginning of stream and soon after a found signal
        if (len(self.data) >= self.BUFFER_LEN):

            self.check4flick()

        ## TEMP: better route than making copies?
        ## issue was that plot would fail early,
        ## i think bc "views" were being passed and deques would change
        ## ie, after x was plotted, y would have a new value appended.
        ## Could also init deques with 1000 zeros. dont like that either.

    def generateSimulatedData(self):
        if len(self.stamps)>1:
            time_passed = self.stamps[-1]-self.stamps[-2]
        else:
            time_passed = None
        high_freq_noise = np.random.normal(0,self.high_freq_noise_var)
        med_freq_noise = self.med_freq_noise(np.random.normal(0,self.med_freq_noise_var),time_passed)
        low_freq_noise = self.low_freq_noise(np.random.normal(0,self.low_freq_noise_var),time_passed)
        signal = 0
        noise = self.baseline_voltage+high_freq_noise+med_freq_noise+low_freq_noise
        return signal+noise

    def triggerSignal(self):
        self.signals.append({'duration':duration,
                             'magnitude':magnitude})

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
        self.signal_magnitude_range = [0.01, 0.02] # volts
        self.


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