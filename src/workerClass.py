
from collections import deque

import serial
import numpy as np
import pyqtgraph as pg
from copy import copy


SERIAL_NAME = '/dev/cu.usbmodem52417201'
BUFFER_LEN = 1000 # n data points kept in buffer
DATA_FNAME = './data.csv'
COLUMNS = ['stamp','data'] # of the output file

# for conversion of input to volts
MAX_ANALOG_VOLTS = 3.3
ANALOG_READ_RESOLUTION = 13 # unique to teensy
raw2volts = lambda x: MAX_ANALOG_VOLTS * x / float(2**ANALOG_READ_RESOLUTION)


class myWorker(pg.QtCore.QObject):
    '''
    Collect data using a QObject so that it can
    be placed on a QThread and run in the background.
    Also saves data if told to.
    '''

    def __init__(self,name=SERIAL_NAME,
                      buffer_len=BUFFER_LEN,
                      saving=False,
                      fname=DATA_FNAME,
                      columns=COLUMNS):

        super(self.__class__,self).__init__()

        self.name = SERIAL_NAME
        self.buffer_len = buffer_len
        self.saving = saving
        self.fname = fname
        self.columns = columns

        # connect to serial
        try: # try to intialize connection with duino
            ## TODO: add timeout and baudrate args
            self.duino = serial.Serial(name)
        except serial.serialutil.SerialException:
            # logging.warning('No serial connection, simulating data')
            self.duino = None

        # initialize empty lists for holding data/time buffers
        self.data = deque(maxlen=self.buffer_len)
        self.stamps = deque(maxlen=self.buffer_len)
        self.pollstamps = deque(maxlen=self.buffer_len)
        ## TEMP just hvae pollstamps for testing
        ## to distinguish poll vs data incoming frequency

        self._startNewFile()

    # signal gets sent to the plotter with each "emit" call
    signal4plot = pg.QtCore.pyqtSignal(deque,deque,deque)
    detect_signal = pg.QtCore.pyqtSignal(int)


    def _startNewFile(self):
        '''initializes file with column names only'''
        with open(self.fname,'w') as newfile:
            newfile.write(','.join(self.columns))

    def _saverow(self,rowlist):
        '''Appends existing file.
        rowlist : 1 value for each column
        '''
        with open(self.fname,'a') as outfile:
            outfile.write('\n'+','.join([ str(x) for x in rowlist ]))


    def keepGrabbingData(self):
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
            vals = [np.random.normal(500,100)] # as list to match receive_serial output
        stamp = serial.time.time()

        ## TODO: currently this only includes the last
        ## _if_ multiple values come thru serial at once
        if len(vals) > 0:
            v = raw2volts(vals[-1])
            # update data buffer
            self.data.append(v)
            self.stamps.append(stamp)
            self.pollstamps.append(stamp)
            # save
            if self.saving:
                self._saverow(rowlist=[stamp,v])
        else:
            # log_and_display('Serial poll came back empty')
            self.pollstamps.append(stamp)
        # send signal to wherever it gets connected to
        self.signal4plot.emit(copy(self.stamps),copy(self.data),copy(self.pollstamps))
        self.detect_signal.emit(copy(self.data))
        ## TEMP: better route than making copies?
        ## issue was that plot would fail early,
        ## i think bc "views" were being passed and deques would change
        ## ie, after x was plotted, y would have a new value appended.
        ## Could also init deques with 1000 zeros. dont like that either.
