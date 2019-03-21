
from collections import deque

from time import time
import pyqtgraph as pg


class myDetector(pg.QtCore.QObject):
    '''Holds main function for signal detection.
    Also keeps track of the time of last detected
    signal, to prevent two signals detected close.
    Requires a duino object to write to if signal found
    '''

    def __init__(self,duino,
                      refractory_len=4,
                      n_vals=100):

        # time to go idle after a detected signal
        self.refract_len = refractory_len # seconds
        # look in last N values from data buffer
        self.n_vals = n_vals 
        self.last_time = 0 # placeholder for time of last signal


    # @pg.QtCore.pyqtSlot(deque) # maybe not necessary
    def check(data):
        '''Look for signal in data passed in.
        '''
        print 'JEREE'
        # skip beginning of stream and soon after a found signal
        if (len(data) > self.n_vals) and (time()-last_time > self.refract_len):
            # grab a subset of data buffer
            data2search = list(islice(reversed(data),0,self.n_vals)) # ugly slice bc of deque
            # check for signal
            flick_found = np.mean(np.diff(data2search)>0) > .5
            if flick_found:
                print 'FOUND ITTTT'
                # log_and_display(win,'Flick detected')
                # send to duino
                # win.myThread.msleep(100)
                # duino.write(bytes(1))
                # time.sleep(1)
                self.last_time = time()


